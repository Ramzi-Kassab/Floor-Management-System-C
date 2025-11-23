from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from inventory.models import Item, Supplier, Location, ConditionType, OwnershipType


class PurchaseRequest(models.Model):
    """Purchase request for items to be ordered."""

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ORDERED', 'Ordered'),
        ('CLOSED', 'Closed'),
    ]

    pr_number = models.CharField(max_length=50, unique=True, help_text="Unique PR number")
    requested_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='purchase_requests'
    )
    request_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date', '-pr_number']
        verbose_name = 'Purchase Request'
        verbose_name_plural = 'Purchase Requests'

    def __str__(self):
        return f"PR {self.pr_number} - {self.status}"


class PurchaseRequestLine(models.Model):
    """Line item for a purchase request."""
    purchase_request = models.ForeignKey(
        PurchaseRequest,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='pr_lines'
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    required_date = models.DateField(null=True, blank=True, help_text="Date when item is needed")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Purchase Request Line'
        verbose_name_plural = 'Purchase Request Lines'

    def __str__(self):
        return f"{self.purchase_request.pr_number} - {self.item.item_code} ({self.quantity})"


class PurchaseOrder(models.Model):
    """Purchase order to supplier."""

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SENT', 'Sent to Supplier'),
        ('PARTIALLY_RECEIVED', 'Partially Received'),
        ('CLOSED', 'Closed'),
        ('CANCELLED', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=50, unique=True, help_text="Unique PO number")
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='purchase_orders'
    )
    order_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    currency = models.CharField(max_length=10, default='USD', help_text="Currency code (USD, EUR, etc.)")
    payment_terms = models.CharField(max_length=200, blank=True, help_text="Payment terms for this PO")
    notes = models.TextField(blank=True)
    external_reference = models.CharField(max_length=100, blank=True, help_text="External ERP PO reference")
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='created_purchase_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-order_date', '-po_number']
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'

    def __str__(self):
        return f"PO {self.po_number} - {self.supplier.name} ({self.status})"


class PurchaseOrderLine(models.Model):
    """Line item for a purchase order."""
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.PROTECT,
        related_name='po_lines'
    )
    ordered_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity ordered from supplier"
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Price per unit in PO currency"
    )
    expected_delivery_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Purchase Order Line'
        verbose_name_plural = 'Purchase Order Lines'

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.item.item_code} ({self.ordered_quantity})"

    @property
    def line_total(self):
        """Calculate line total."""
        return self.ordered_quantity * self.unit_price


class GoodsReceipt(models.Model):
    """Goods receipt note for received items."""
    grn_number = models.CharField(max_length=50, unique=True, help_text="Unique GRN number")
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.PROTECT,
        related_name='goods_receipts'
    )
    receipt_date = models.DateField()
    received_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='goods_receipts'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-receipt_date', '-grn_number']
        verbose_name = 'Goods Receipt'
        verbose_name_plural = 'Goods Receipts'

    def __str__(self):
        return f"GRN {self.grn_number} - PO {self.purchase_order.po_number}"


class GoodsReceiptLine(models.Model):
    """Line item for goods receipt."""
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.CASCADE,
        related_name='lines'
    )
    purchase_order_line = models.ForeignKey(
        PurchaseOrderLine,
        on_delete=models.PROTECT,
        related_name='receipt_lines'
    )
    received_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity actually received"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='receipt_lines',
        help_text="Storage location for received items"
    )
    condition_type = models.ForeignKey(
        ConditionType,
        on_delete=models.PROTECT,
        related_name='receipt_lines',
        help_text="Condition of received items"
    )
    ownership_type = models.ForeignKey(
        OwnershipType,
        on_delete=models.PROTECT,
        related_name='receipt_lines',
        help_text="Ownership type of received items"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Goods Receipt Line'
        verbose_name_plural = 'Goods Receipt Lines'

    def __str__(self):
        return f"{self.goods_receipt.grn_number} - {self.purchase_order_line.item.item_code} ({self.received_quantity})"

    def save(self, *args, **kwargs):
        """
        Override save to create stock transaction and update stock level.
        This creates a PURCHASE_RECEIPT transaction when a GRN line is saved.
        """
        from inventory.models import StockLevel, StockTransaction

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Create stock transaction
            StockTransaction.objects.create(
                item=self.purchase_order_line.item,
                from_location=None,
                to_location=self.location,
                condition_type=self.condition_type,
                ownership_type=self.ownership_type,
                transaction_type='PURCHASE_RECEIPT',
                quantity=self.received_quantity,
                reference=self.goods_receipt.grn_number,
                performed_by=self.goods_receipt.received_by,
                notes=f"GRN {self.goods_receipt.grn_number} - PO {self.goods_receipt.purchase_order.po_number}"
            )

            # Update or create stock level
            stock_level, created = StockLevel.objects.get_or_create(
                item=self.purchase_order_line.item,
                location=self.location,
                condition_type=self.condition_type,
                ownership_type=self.ownership_type,
                defaults={'quantity': 0}
            )
            stock_level.quantity += self.received_quantity
            stock_level.save()


# ==================== Goods Return (RTV - Return to Vendor) ====================

class GoodsReturn(models.Model):
    """
    Goods Return Note (GRN Return) for returning items to suppliers.
    Handles scenarios like wrong items, damaged goods, excess quantity, etc.
    """
    
    RETURN_REASON_CHOICES = [
        ('WRONG_ITEM', 'Wrong Item Received'),
        ('WRONG_QUANTITY', 'Excess Quantity'),
        ('DAMAGED', 'Damaged on Arrival'),
        ('DEFECTIVE', 'Defective/Quality Issue'),
        ('NOT_ORDERED', 'Not Ordered'),
        ('EXPIRED', 'Expired or Near Expiry'),
        ('OTHER', 'Other Reason'),
    ]
    
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted to Supplier'),
        ('APPROVED', 'Approved by Supplier'),
        ('REJECTED', 'Rejected by Supplier'),
        ('PICKED_UP', 'Picked Up by Supplier'),
        ('CREDITED', 'Credit Note Received'),
        ('CLOSED', 'Closed'),
    ]
    
    rtn_number = models.CharField(max_length=50, unique=True, help_text="Return Number (RTN)")
    goods_receipt = models.ForeignKey(
        GoodsReceipt,
        on_delete=models.PROTECT,
        related_name='returns',
        help_text="Original GRN being returned"
    )
    return_date = models.DateField(help_text="Date of return")
    return_reason = models.CharField(
        max_length=20,
        choices=RETURN_REASON_CHOICES,
        help_text="Reason for return"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    returned_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='goods_returns'
    )
    supplier_contact = models.CharField(max_length=200, blank=True, help_text="Supplier contact person")
    supplier_approval_ref = models.CharField(max_length=100, blank=True, help_text="Supplier's RMA/approval reference")
    credit_note_number = models.CharField(max_length=100, blank=True, help_text="Supplier's credit note number")
    credit_note_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-return_date', '-rtn_number']
        verbose_name = 'Goods Return'
        verbose_name_plural = 'Goods Returns'
    
    def __str__(self):
        return f"RTN {self.rtn_number} - {self.get_return_reason_display()}"
    
    @property
    def total_return_value(self):
        """Calculate total value of returned items."""
        total = sum(
            line.return_quantity * line.unit_price
            for line in self.return_lines.all()
        )
        return total


class GoodsReturnLine(models.Model):
    """Line item for goods return."""
    
    goods_return = models.ForeignKey(
        GoodsReturn,
        on_delete=models.CASCADE,
        related_name='return_lines'
    )
    goods_receipt_line = models.ForeignKey(
        GoodsReceiptLine,
        on_delete=models.PROTECT,
        related_name='returns',
        help_text="Original GRN line being returned"
    )
    return_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity being returned"
    )
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0'),
        help_text="Unit price for value calculation"
    )
    condition_at_return = models.ForeignKey(
        ConditionType,
        on_delete=models.PROTECT,
        related_name='return_lines',
        help_text="Condition of items being returned"
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='return_lines',
        help_text="Location from which items are being returned"
    )
    notes = models.TextField(blank=True, help_text="Notes about this return line")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
        verbose_name = 'Goods Return Line'
        verbose_name_plural = 'Goods Return Lines'
    
    def __str__(self):
        return f"{self.goods_return.rtn_number} - {self.goods_receipt_line.purchase_order_line.item.item_code} ({self.return_quantity})"
    
    @property
    def item(self):
        """Get the item from the original GRN line."""
        return self.goods_receipt_line.purchase_order_line.item
    
    @property
    def line_value(self):
        """Calculate line value."""
        return self.return_quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        """
        Override save to create stock transaction and update stock level.
        This creates a RETURN_TO_VENDOR transaction when a return line is saved.
        """
        from inventory.models import StockLevel, StockTransaction
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and self.goods_return.status in ['SUBMITTED', 'APPROVED', 'PICKED_UP']:
            # Create stock transaction (negative quantity for return)
            StockTransaction.objects.create(
                item=self.item,
                from_location=self.location,
                to_location=None,
                condition_type=self.condition_at_return,
                ownership_type=self.goods_receipt_line.ownership_type,
                transaction_type='RETURN_TO_VENDOR',
                quantity=-self.return_quantity,  # Negative for return
                reference=self.goods_return.rtn_number,
                performed_by=self.goods_return.returned_by,
                notes=f"Return {self.goods_return.rtn_number} - Reason: {self.goods_return.get_return_reason_display()}"
            )
            
            # Update stock level (decrease stock)
            try:
                stock_level = StockLevel.objects.get(
                    item=self.item,
                    location=self.location,
                    condition_type=self.condition_at_return,
                    ownership_type=self.goods_receipt_line.ownership_type
                )
                stock_level.quantity -= self.return_quantity
                stock_level.save()
            except StockLevel.DoesNotExist:
                # This shouldn't happen, but log it
                pass


# ==================== GRN Correction ====================

class GRNCorrection(models.Model):
    """
    Correction record for GRN errors (wrong quantity, wrong item, etc.).
    This creates adjusting transactions without deleting the original GRN.
    """
    
    CORRECTION_TYPE_CHOICES = [
        ('QUANTITY_OVERCOUNT', 'Quantity Overcounted'),
        ('QUANTITY_UNDERCOUNT', 'Quantity Undercounted'),
        ('WRONG_ITEM', 'Wrong Item Recorded'),
        ('WRONG_LOCATION', 'Wrong Location'),
        ('WRONG_CONDITION', 'Wrong Condition Type'),
        ('OTHER', 'Other Correction'),
    ]
    
    correction_number = models.CharField(max_length=50, unique=True, help_text="Unique correction reference")
    goods_receipt_line = models.ForeignKey(
        GoodsReceiptLine,
        on_delete=models.PROTECT,
        related_name='corrections',
        help_text="GRN line being corrected"
    )
    correction_type = models.CharField(
        max_length=30,
        choices=CORRECTION_TYPE_CHOICES
    )
    correction_date = models.DateField()
    corrected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='grn_corrections'
    )
    
    # Original values (for reference)
    original_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Original received quantity"
    )
    original_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='original_grn_corrections',
        null=True,
        blank=True
    )
    
    # Corrected values
    corrected_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Corrected quantity (if quantity correction)"
    )
    corrected_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        related_name='corrected_grn_corrections',
        null=True,
        blank=True,
        help_text="Corrected location (if location correction)"
    )
    corrected_condition = models.ForeignKey(
        ConditionType,
        on_delete=models.PROTECT,
        related_name='grn_corrections',
        null=True,
        blank=True,
        help_text="Corrected condition (if condition correction)"
    )
    
    reason = models.TextField(help_text="Detailed reason for correction")
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_grn_corrections'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-correction_date', '-correction_number']
        verbose_name = 'GRN Correction'
        verbose_name_plural = 'GRN Corrections'
    
    def __str__(self):
        return f"Correction {self.correction_number} - {self.get_correction_type_display()}"
    
    @property
    def adjustment_quantity(self):
        """Calculate the quantity adjustment (positive or negative)."""
        if self.corrected_quantity is not None:
            return self.corrected_quantity - self.original_quantity
        return Decimal('0')
    
    def apply_correction(self):
        """
        Apply the correction by creating adjusting stock transactions.
        Should only be called when correction is approved.
        """
        from inventory.models import StockLevel, StockTransaction
        
        if not self.approved:
            raise ValueError("Cannot apply unapproved correction")
        
        item = self.goods_receipt_line.purchase_order_line.item
        
        if self.correction_type in ['QUANTITY_OVERCOUNT', 'QUANTITY_UNDERCOUNT'] and self.corrected_quantity is not None:
            # Quantity correction - create adjustment transaction
            adjustment_qty = self.adjustment_quantity
            
            if adjustment_qty != 0:
                StockTransaction.objects.create(
                    item=item,
                    to_location=self.goods_receipt_line.location,
                    condition_type=self.goods_receipt_line.condition_type,
                    ownership_type=self.goods_receipt_line.ownership_type,
                    transaction_type='ADJUSTMENT',
                    quantity=adjustment_qty,
                    reference=self.correction_number,
                    performed_by=self.corrected_by,
                    notes=f"GRN Correction: {self.get_correction_type_display()} for GRN {self.goods_receipt_line.goods_receipt.grn_number}"
                )
                
                # Update stock level
                stock_level, created = StockLevel.objects.get_or_create(
                    item=item,
                    location=self.goods_receipt_line.location,
                    condition_type=self.goods_receipt_line.condition_type,
                    ownership_type=self.goods_receipt_line.ownership_type,
                    defaults={'quantity': Decimal('0')}
                )
                stock_level.quantity += adjustment_qty
                stock_level.save()
        
        elif self.correction_type == 'WRONG_LOCATION' and self.corrected_location:
            # Location correction - transfer stock
            StockTransaction.objects.create(
                item=item,
                from_location=self.original_location,
                to_location=self.corrected_location,
                condition_type=self.goods_receipt_line.condition_type,
                ownership_type=self.goods_receipt_line.ownership_type,
                transaction_type='TRANSFER',
                quantity=self.original_quantity,
                reference=self.correction_number,
                performed_by=self.corrected_by,
                notes=f"GRN Location Correction for {self.goods_receipt_line.goods_receipt.grn_number}"
            )
            
            # Decrease from original location
            try:
                stock_level = StockLevel.objects.get(
                    item=item,
                    location=self.original_location,
                    condition_type=self.goods_receipt_line.condition_type,
                    ownership_type=self.goods_receipt_line.ownership_type
                )
                stock_level.quantity -= self.original_quantity
                stock_level.save()
            except StockLevel.DoesNotExist:
                pass
            
            # Increase in corrected location
            stock_level, created = StockLevel.objects.get_or_create(
                item=item,
                location=self.corrected_location,
                condition_type=self.goods_receipt_line.condition_type,
                ownership_type=self.goods_receipt_line.ownership_type,
                defaults={'quantity': Decimal('0')}
            )
            stock_level.quantity += self.original_quantity
            stock_level.save()
