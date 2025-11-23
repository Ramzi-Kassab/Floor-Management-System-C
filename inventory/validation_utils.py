"""
Validation utilities for inventory operations.
Prevents common errors and provides approval workflows.
"""
from decimal import Decimal
from django.core.exceptions import ValidationError
from .models import Item, Location, StockLevel, StockTransaction
import re


class StockOperationValidator:
    """
    Validates stock operations to prevent common errors.
    """

    @staticmethod
    def validate_qr_code(qr_data, expected_type='ITEM'):
        """
        Validate scanned QR code data.
        Expected format: TYPE:CODE|NAME|...
        Example: ITEM:ITM-001|Cutter|CUTTER
        """
        if not qr_data:
            raise ValidationError("QR code data is empty")

        parts = qr_data.split(':')
        if len(parts) < 2:
            raise ValidationError(
                "Invalid QR code format. Expected format: TYPE:CODE|..."
            )

        scanned_type = parts[0].upper()
        if scanned_type != expected_type:
            raise ValidationError(
                f"Wrong QR code type. Expected {expected_type}, got {scanned_type}"
            )

        # Extract code from data
        data_parts = parts[1].split('|')
        if not data_parts[0]:
            raise ValidationError("QR code contains no item/location code")

        code = data_parts[0]

        # Verify the item/location exists
        if expected_type == 'ITEM':
            try:
                item = Item.objects.get(item_code=code)
                return item
            except Item.DoesNotExist:
                raise ValidationError(
                    f"Item with code '{code}' not found in system. "
                    f"This QR code may be from a different system or outdated."
                )
        elif expected_type == 'LOCATION':
            try:
                location = Location.objects.get(code=code)
                return location
            except Location.DoesNotExist:
                raise ValidationError(
                    f"Location with code '{code}' not found in system."
                )

        return code

    @staticmethod
    def validate_quantity(quantity, item, operation_type='ADJUSTMENT'):
        """
        Validate quantity for stock operations.
        Checks for:
        - Negative quantities (where not allowed)
        - Unreasonably large quantities (potential data entry error)
        - Decimal places matching item UOM precision
        """
        if quantity is None:
            raise ValidationError("Quantity is required")

        quantity = Decimal(str(quantity))

        # Check for unreasonably large quantities (potential extra digit)
        # Flag if quantity > 10000 units
        if abs(quantity) > 10000:
            raise ValidationError(
                f"Quantity {quantity} seems unusually large. "
                f"Please verify: Did you mean {quantity/10}? "
                f"If this is correct, contact supervisor for approval."
            )

        # Check decimal places (max 2 decimal places for most items)
        decimal_places = abs(quantity.as_tuple().exponent)
        if decimal_places > 2:
            raise ValidationError(
                f"Quantity has too many decimal places ({decimal_places}). "
                f"Maximum allowed is 2 decimal places."
            )

        # For specific operations, check if negative is allowed
        if operation_type in ['ISSUE', 'TRANSFER', 'RETURN_TO_VENDOR']:
            if quantity < 0:
                raise ValidationError(
                    f"Negative quantities not allowed for {operation_type}"
                )

        return quantity

    @staticmethod
    def check_stock_availability(item, location, condition_type, ownership_type, required_quantity):
        """
        Check if sufficient stock is available for the operation.
        Returns (available_quantity, is_sufficient, shortage_quantity)
        """
        try:
            stock_level = StockLevel.objects.get(
                item=item,
                location=location,
                condition_type=condition_type,
                ownership_type=ownership_type
            )
            available = stock_level.quantity
        except StockLevel.DoesNotExist:
            available = Decimal('0')

        is_sufficient = available >= required_quantity
        shortage = max(Decimal('0'), required_quantity - available)

        return available, is_sufficient, shortage

    @staticmethod
    def validate_stock_operation(item, from_location, to_location, condition_type,
                                 ownership_type, quantity, operation_type):
        """
        Comprehensive validation for stock operations.
        Returns (is_valid, errors, warnings)
        """
        errors = []
        warnings = []

        # Validate quantity
        try:
            quantity = StockOperationValidator.validate_quantity(
                quantity, item, operation_type
            )
        except ValidationError as e:
            errors.append(str(e))
            return False, errors, warnings

        # For operations that remove stock, check availability
        if operation_type in ['TRANSFER', 'ISSUE', 'RETURN_TO_VENDOR'] and from_location:
            available, is_sufficient, shortage = StockOperationValidator.check_stock_availability(
                item, from_location, condition_type, ownership_type, quantity
            )

            if not is_sufficient:
                errors.append(
                    f"Insufficient stock. Available: {available}, "
                    f"Required: {quantity}, Shortage: {shortage}"
                )

            # Warning for low stock after operation
            remaining = available - quantity
            if remaining < item.reorder_level * Decimal('0.25'):  # Below 25% of reorder
                warnings.append(
                    f"Warning: After this operation, stock will be {remaining} "
                    f"(critically low, reorder level: {item.reorder_level})"
                )

        # Check for same location transfer
        if operation_type == 'TRANSFER' and from_location == to_location:
            errors.append("Cannot transfer to the same location")

        is_valid = len(errors) == 0
        return is_valid, errors, warnings


class ApprovalWorkflow:
    """
    Manages approval workflows for stock operations.
    """

    # Operations that require supervisor approval
    REQUIRES_APPROVAL = [
        'LARGE_ADJUSTMENT',  # Adjustments > 100 units or > reorder level
        'NEGATIVE_STOCK',    # Operations resulting in negative stock
        'HIGH_VALUE',        # High value items
        'DISCREPANCY',       # Large discrepancies in count
    ]

    @staticmethod
    def requires_supervisor_approval(operation_type, quantity, item, current_stock=None):
        """
        Determine if operation requires supervisor approval.
        Returns (requires_approval, reason)
        """
        quantity = abs(Decimal(str(quantity)))

        # Large adjustments
        if operation_type in ['ADJUSTMENT', 'WRITE_OFF']:
            if quantity > 100:
                return True, "Quantity exceeds 100 units"
            if quantity > item.reorder_level:
                return True, f"Quantity exceeds reorder level ({item.reorder_level})"

        # Would result in negative stock
        if current_stock is not None and current_stock < 0:
            return True, "Operation would result in negative stock"

        # Large discrepancy (> 20% difference)
        if operation_type == 'RECONCILIATION' and current_stock is not None:
            if quantity > 0:
                discrepancy_pct = abs(current_stock - quantity) / max(quantity, Decimal('1')) * 100
                if discrepancy_pct > 20:
                    return True, f"Discrepancy exceeds 20% ({discrepancy_pct:.1f}%)"

        return False, None

    @staticmethod
    def create_approval_request(transaction, requested_by, reason):
        """
        Create an approval request for a stock operation.
        Returns approval request object.
        """
        from .models import StockOperationApproval

        approval = StockOperationApproval.objects.create(
            transaction=transaction,
            requested_by=requested_by,
            reason_for_request=reason,
            status='PENDING'
        )

        return approval


class DataEntryValidator:
    """
    Validates data entry to catch common mistakes.
    """

    @staticmethod
    def check_duplicate_entry(item, location, transaction_type, quantity, time_window_minutes=5):
        """
        Check if this might be a duplicate entry within time window.
        Returns (is_likely_duplicate, similar_transaction)
        """
        from django.utils import timezone
        from datetime import timedelta

        cutoff_time = timezone.now() - timedelta(minutes=time_window_minutes)

        similar_transactions = StockTransaction.objects.filter(
            item=item,
            to_location=location,
            transaction_type=transaction_type,
            quantity=quantity,
            performed_at__gte=cutoff_time
        ).order_by('-performed_at')

        if similar_transactions.exists():
            return True, similar_transactions.first()

        return False, None

    @staticmethod
    def validate_item_location_compatibility(item, location):
        """
        Check if item type is compatible with location type.
        For example, powder items should go to silo locations.
        """
        warnings = []

        # Example business rules (customize as needed)
        if item.item_type == 'MATRIX_POWDER' and 'SILO' not in location.code.upper():
            warnings.append(
                f"Warning: Powder items are typically stored in SILO locations. "
                f"Location {location.code} may not be suitable."
            )

        if item.item_type == 'CUTTER' and 'RACK' not in location.code.upper():
            warnings.append(
                f"Warning: Cutters are typically stored in RACK locations."
            )

        return warnings

    @staticmethod
    def suggest_correction(entered_value, expected_value_range):
        """
        Suggest possible correction for data entry errors.
        For example, if user entered 1000 instead of 100.
        """
        entered = Decimal(str(entered_value))
        min_expected, max_expected = expected_value_range

        suggestions = []

        # Check if extra zero was added
        if entered == Decimal(str(max_expected)) * 10:
            suggestions.append(
                f"Did you mean {max_expected}? (Extra zero may have been entered)"
            )

        # Check if decimal point was missed
        if entered == Decimal(str(max_expected)) * 100:
            suggestions.append(
                f"Did you mean {max_expected}? (Decimal point may be missing)"
            )

        return suggestions
