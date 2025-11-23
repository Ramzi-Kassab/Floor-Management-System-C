from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from datetime import date, datetime, timedelta
from django.utils import timezone
import base64

from .models import (
    Supplier, ItemCategory, UnitOfMeasure, Item,
    Warehouse, Location, ConditionType, OwnershipType,
    StockLevel, StockTransaction, StockOperationApproval
)
from .quality_control import (
    QualityInspection, ItemBatch, DefectiveItemDisposition,
    UsedItemTracking, ExpiredItemAction
)
from .ksa_compliance import (
    CompanyProfile, ItemCertificate, CustomsDeclaration,
    CustomsDeclarationLine, Shipment
)
from . import ksa_utils
from .validation_utils import StockOperationValidator, ApprovalWorkflow, DataEntryValidator


class SupplierModelTest(TestCase):
    def setUp(self):
        self.supplier = Supplier.objects.create(
            code='SUP-001',
            name='Test Supplier',
            country='USA',
            email='test@supplier.com',
            active=True
        )

    def test_supplier_str(self):
        self.assertEqual(str(self.supplier), 'SUP-001 - Test Supplier')

    def test_supplier_creation(self):
        self.assertEqual(self.supplier.code, 'SUP-001')
        self.assertTrue(self.supplier.active)


class ItemModelTest(TestCase):
    def setUp(self):
        self.category = ItemCategory.objects.create(
            code='TEST-CAT',
            name='Test Category'
        )
        self.uom = UnitOfMeasure.objects.create(
            code='EA',
            name='Each',
            is_base_unit=True
        )
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom,
            item_type='OTHER',
            reorder_level=Decimal('10.00')
        )

    def test_item_str(self):
        self.assertEqual(str(self.item), 'ITEM-001 - Test Item')

    def test_item_creation(self):
        self.assertEqual(self.item.item_code, 'ITEM-001')
        self.assertEqual(self.item.reorder_level, Decimal('10.00'))
        self.assertTrue(self.item.active)


class WarehouseAndLocationTest(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(
            code='WH-01',
            name='Main Warehouse',
            active=True
        )
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-A1',
            name='Location A1',
            is_virtual=False
        )

    def test_warehouse_str(self):
        self.assertEqual(str(self.warehouse), 'WH-01 - Main Warehouse')

    def test_location_str(self):
        expected = 'WH-01 > LOC-A1 - Location A1'
        self.assertEqual(str(self.location), expected)

    def test_location_belongs_to_warehouse(self):
        self.assertEqual(self.location.warehouse, self.warehouse)


class StockLevelTest(TestCase):
    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Warehouse', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-A1',
            name='Location A1'
        )
        self.condition = ConditionType.objects.create(code='NEW', name='New')
        self.ownership = OwnershipType.objects.create(code='OWN', name='Own')

    def test_stock_level_creation(self):
        stock = StockLevel.objects.create(
            item=self.item,
            location=self.location,
            condition_type=self.condition,
            ownership_type=self.ownership,
            quantity=Decimal('100.00')
        )
        self.assertEqual(stock.quantity, Decimal('100.00'))

    def test_unique_constraint(self):
        """Test that we cannot create duplicate stock levels."""
        StockLevel.objects.create(
            item=self.item,
            location=self.location,
            condition_type=self.condition,
            ownership_type=self.ownership,
            quantity=Decimal('50.00')
        )
        # This should raise an IntegrityError due to unique_together constraint
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            StockLevel.objects.create(
                item=self.item,
                location=self.location,
                condition_type=self.condition,
                ownership_type=self.ownership,
                quantity=Decimal('100.00')
            )


class StockTransactionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Warehouse', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-A1',
            name='Location A1'
        )
        self.condition = ConditionType.objects.create(code='NEW', name='New')
        self.ownership = OwnershipType.objects.create(code='OWN', name='Own')

    def test_adjustment_transaction(self):
        """Test creating an adjustment transaction."""
        transaction = StockTransaction.objects.create(
            item=self.item,
            to_location=self.location,
            condition_type=self.condition,
            ownership_type=self.ownership,
            transaction_type='ADJUSTMENT',
            quantity=Decimal('50.00'),
            reference='ADJ-001',
            performed_by=self.user
        )
        self.assertEqual(transaction.transaction_type, 'ADJUSTMENT')
        self.assertEqual(transaction.quantity, Decimal('50.00'))
        self.assertIsNone(transaction.from_location)

    def test_transfer_transaction(self):
        """Test creating a transfer transaction."""
        location2 = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-B1',
            name='Location B1'
        )
        transaction = StockTransaction.objects.create(
            item=self.item,
            from_location=self.location,
            to_location=location2,
            condition_type=self.condition,
            ownership_type=self.ownership,
            transaction_type='TRANSFER',
            quantity=Decimal('25.00'),
            reference='TRF-001',
            performed_by=self.user
        )
        self.assertEqual(transaction.transaction_type, 'TRANSFER')
        self.assertIsNotNone(transaction.from_location)
        self.assertIsNotNone(transaction.to_location)


# ==================== KSA Utilities Tests ====================

class KSAUtilsTestCase(TestCase):
    """Test KSA utility functions."""

    def test_zatca_qr_code_generation(self):
        """Test ZATCA QR code generation and decoding."""
        qr_data = ksa_utils.generate_zatca_qr_code(
            seller_name="Test Drilling Company",
            vat_number="300012345600003",
            timestamp="2025-11-23T15:30:00Z",
            total_with_vat=1150.00,
            vat_amount=150.00
        )

        # Should return base64 encoded string
        self.assertIsNotNone(qr_data)
        self.assertIsInstance(qr_data, str)

        # Verify it's valid base64
        try:
            base64.b64decode(qr_data)
            is_valid_base64 = True
        except:
            is_valid_base64 = False
        self.assertTrue(is_valid_base64)

        # Test decoding
        decoded = ksa_utils.decode_zatca_qr_code(qr_data)
        self.assertEqual(decoded['seller_name'], "Test Drilling Company")
        self.assertEqual(decoded['vat_number'], "300012345600003")
        self.assertEqual(decoded['total_with_vat'], "1150.00")
        self.assertEqual(decoded['vat_amount'], "150.00")

    def test_vat_number_validation_valid(self):
        """Test valid Saudi VAT numbers."""
        valid_numbers = [
            "300012345600003",
            "300-0123-4560-0003",
            "311234567890123"
        ]

        for vat_num in valid_numbers:
            is_valid, error = ksa_utils.validate_saudi_vat_number(vat_num)
            self.assertTrue(is_valid, f"{vat_num} should be valid")
            self.assertIsNone(error)

    def test_vat_number_validation_invalid(self):
        """Test invalid Saudi VAT numbers."""
        invalid_numbers = [
            ("12345", "VAT number must be 15 digits"),
            ("400012345600003", "VAT number must start with 3"),
            ("30001234560000X", "VAT number must contain only digits"),
            ("", "VAT number is required"),
        ]

        for vat_num, expected_error_substring in invalid_numbers:
            is_valid, error = ksa_utils.validate_saudi_vat_number(vat_num)
            self.assertFalse(is_valid)
            self.assertIn(expected_error_substring, error)

    def test_vat_number_formatting(self):
        """Test VAT number formatting."""
        formatted = ksa_utils.format_saudi_vat_number("300012345600003")
        self.assertEqual(formatted, "300-0123-4560-0003")

    def test_hs_code_validation(self):
        """Test HS code validation."""
        # Valid 10-digit HS code
        is_valid, error = ksa_utils.validate_hs_code("8207130000")
        self.assertTrue(is_valid)
        self.assertIsNone(error)

        # Invalid - too short
        is_valid, error = ksa_utils.validate_hs_code("820713")
        self.assertFalse(is_valid)
        self.assertIn("must be 10 digits", error)

        # Invalid - contains letters
        is_valid, error = ksa_utils.validate_hs_code("820713000A")
        self.assertFalse(is_valid)
        self.assertIn("only digits", error)

    def test_hs_code_formatting(self):
        """Test HS code formatting."""
        formatted = ksa_utils.format_hs_code("8207130000")
        self.assertEqual(formatted, "8207.13.00.00")

    def test_vat_calculations(self):
        """Test VAT calculation functions."""
        # Calculate VAT on base amount
        vat = ksa_utils.calculate_vat_amount(Decimal('1000.00'))
        self.assertEqual(vat, Decimal('150.00'))

        # Calculate total including VAT
        total = ksa_utils.calculate_amount_including_vat(Decimal('1000.00'))
        self.assertEqual(total, Decimal('1150.00'))

        # Extract VAT from total
        base, vat = ksa_utils.extract_vat_from_total(Decimal('1150.00'))
        self.assertAlmostEqual(float(base), 1000.00, places=2)
        self.assertAlmostEqual(float(vat), 150.00, places=2)

    def test_zakat_calculation(self):
        """Test Zakat calculation (2.5%)."""
        zakat = ksa_utils.calculate_zakat(Decimal('100000.00'))
        self.assertEqual(zakat, Decimal('2500.00'))

    def test_postal_code_validation(self):
        """Test Saudi postal code validation."""
        # Valid
        is_valid, error = ksa_utils.validate_saudi_postal_code("12345")
        self.assertTrue(is_valid)

        # Invalid - wrong length
        is_valid, error = ksa_utils.validate_saudi_postal_code("123")
        self.assertFalse(is_valid)
        self.assertIn("5 digits", error)

    def test_phone_number_validation(self):
        """Test Saudi phone number validation."""
        # Valid mobile numbers
        valid_mobile = [
            "0512345678",
            "+966512345678",
            "966512345678"
        ]
        for phone in valid_mobile:
            is_valid, error, phone_type = ksa_utils.validate_saudi_phone_number(phone)
            self.assertTrue(is_valid, f"{phone} should be valid")
            self.assertEqual(phone_type, 'mobile')

        # Valid landline
        is_valid, error, phone_type = ksa_utils.validate_saudi_phone_number("0112345678")
        self.assertTrue(is_valid)
        self.assertEqual(phone_type, 'landline')

        # Invalid
        is_valid, error, phone_type = ksa_utils.validate_saudi_phone_number("123")
        self.assertFalse(is_valid)

    def test_arabic_numeral_conversion(self):
        """Test conversion to Arabic-Indic numerals."""
        result = ksa_utils.convert_to_arabic_numerals("12345")
        self.assertEqual(result, "١٢٣٤٥")

    def test_currency_formatting_arabic(self):
        """Test Arabic currency formatting."""
        formatted = ksa_utils.format_currency_arabic(1150.50)
        self.assertIn("ر.س", formatted)  # SAR symbol
        self.assertIn("٫", formatted)    # Arabic decimal separator


# ==================== KSA Compliance Models Tests ====================

class CompanyProfileModelTest(TestCase):
    """Test CompanyProfile model."""

    def test_company_profile_creation(self):
        """Test creating a company profile."""
        profile = CompanyProfile.objects.create(
            company_name_en="Drilling Bits Manufacturing Co.",
            company_name_ar="شركة تصنيع البتات للحفر",
            commercial_registration="1234567890",
            vat_registration_number="300012345600003",
            city="Dammam",
            country="SA"
        )

        self.assertEqual(profile.country, "SA")
        self.assertTrue(profile.einvoice_enabled)

    def test_company_profile_str(self):
        """Test string representation."""
        profile = CompanyProfile.objects.create(
            company_name_en="Test Co.",
            commercial_registration="1234567890",
            vat_registration_number="300012345600003",
        )

        self.assertIn("Test Co.", str(profile))


class ItemCertificateModelTest(TestCase):
    """Test ItemCertificate model."""

    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Drill Bit',
            category=self.category,
            unit_of_measure=self.uom
        )

    def test_certificate_creation(self):
        """Test creating an item certificate."""
        cert = ItemCertificate.objects.create(
            item=self.item,
            certificate_type='SABER',
            certificate_number='SABER-2025-12345',
            issue_date=date(2025, 1, 1),
            expiry_date=date(2026, 1, 1),
            status='VALID'
        )

        self.assertEqual(cert.certificate_type, 'SABER')
        self.assertEqual(cert.status, 'VALID')

    def test_certificate_expiry_checking(self):
        """Test expiry date checking."""
        # Expiring soon (within 30 days)
        expiry_soon = date.today() + timedelta(days=15)
        cert = ItemCertificate.objects.create(
            item=self.item,
            certificate_type='SABER',
            certificate_number='SABER-123',
            issue_date=date.today() - timedelta(days=100),
            expiry_date=expiry_soon,
            status='VALID'
        )

        self.assertTrue(cert.is_expiring_soon)
        self.assertIsNotNone(cert.days_until_expiry)
        self.assertLess(cert.days_until_expiry, 30)

    def test_expired_certificate(self):
        """Test expired certificate."""
        cert = ItemCertificate.objects.create(
            item=self.item,
            certificate_type='SASO',
            certificate_number='SASO-123',
            issue_date=date(2023, 1, 1),
            expiry_date=date(2024, 1, 1),
            status='EXPIRED'
        )

        self.assertLess(cert.days_until_expiry, 0)


class CustomsDeclarationModelTest(TestCase):
    """Test CustomsDeclaration and CustomsDeclarationLine models."""

    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Drill Bit',
            category=self.category,
            unit_of_measure=self.uom,
            hs_code='8207130000'
        )
        self.supplier = Supplier.objects.create(
            code='SUP-001',
            name='Foreign Supplier',
            country='US'
        )

    def test_customs_declaration_creation(self):
        """Test creating a customs declaration."""
        declaration = CustomsDeclaration.objects.create(
            declaration_number='FASAH-2025-001',
            supplier=self.supplier,
            bill_of_lading='BOL-12345',
            port_of_entry='Jeddah Islamic Port',
            declaration_date=date.today(),
            clearance_status='PENDING',
            total_customs_duty=Decimal('500.00'),
            total_vat=Decimal('750.00'),
            other_fees=Decimal('50.00')
        )

        self.assertEqual(declaration.clearance_status, 'PENDING')
        # Test total amount calculation
        self.assertEqual(
            declaration.total_amount_payable,
            Decimal('500.00') + Decimal('750.00') + Decimal('50.00')
        )

    def test_customs_declaration_line_duty_calculation(self):
        """Test customs duty and VAT calculation."""
        declaration = CustomsDeclaration.objects.create(
            declaration_number='FASAH-2025-002',
            supplier=self.supplier,
            bill_of_lading='BOL-12346',
            port_of_entry='Dammam',
            declaration_date=date.today(),
            clearance_status='CLEARED'
        )

        line = CustomsDeclarationLine.objects.create(
            customs_declaration=declaration,
            item=self.item,
            quantity=Decimal('100'),
            unit_price=Decimal('50.00'),
            total_value=Decimal('5000.00'),
            hs_code='8207130000',
            customs_duty_rate=Decimal('5.00'),  # 5%
            vat_rate=Decimal('15.00')  # 15%
        )

        # Calculate duties
        line.calculate_duties()

        # Customs duty = 5000 * 5% = 250
        self.assertEqual(line.customs_duty_amount, Decimal('250.00'))

        # VAT = (5000 + 250) * 15% = 787.50
        self.assertEqual(line.vat_amount, Decimal('787.50'))


class ShipmentModelTest(TestCase):
    """Test Shipment model."""

    def test_shipment_creation(self):
        """Test creating a shipment."""
        shipment = Shipment.objects.create(
            shipment_number='SHIP-2025-001',
            carrier='SMSA',
            tracking_number='SMSA123456789',
            origin='Riyadh',
            destination='Jeddah',
            shipment_date=date.today(),
            status='IN_TRANSIT',
            estimated_delivery=date.today() + timedelta(days=2)
        )

        self.assertEqual(shipment.carrier, 'SMSA')
        self.assertEqual(shipment.status, 'IN_TRANSIT')


# ==================== Quality Control Models Tests ====================

class QualityInspectionModelTest(TestCase):
    """Test QualityInspection model."""

    def setUp(self):
        self.user = User.objects.create_user(username='inspector', password='12345')
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Drill Bit',
            category=self.category,
            unit_of_measure=self.uom
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Main', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='QC-AREA',
            name='QC Area'
        )

    def test_quality_inspection_creation(self):
        """Test creating a quality inspection."""
        inspection = QualityInspection.objects.create(
            inspection_number='QC-2025-001',
            item=self.item,
            location=self.location,
            quantity_inspected=Decimal('100'),
            inspection_date=date.today(),
            inspector=self.user,
            inspection_result='PASS',
            passed_quantity=Decimal('98'),
            failed_quantity=Decimal('2')
        )

        self.assertEqual(inspection.inspection_result, 'PASS')
        self.assertEqual(inspection.passed_quantity, Decimal('98'))

    def test_inspection_with_defects(self):
        """Test inspection with defects."""
        inspection = QualityInspection.objects.create(
            inspection_number='QC-2025-002',
            item=self.item,
            location=self.location,
            quantity_inspected=Decimal('50'),
            inspection_date=date.today(),
            inspector=self.user,
            inspection_result='REJECT',
            passed_quantity=Decimal('0'),
            failed_quantity=Decimal('50'),
            defect_category='DIMENSIONAL',
            defect_severity='CRITICAL',
            defect_description='Out of tolerance',
            disposition='RETURN_TO_VENDOR'
        )

        self.assertEqual(inspection.defect_severity, 'CRITICAL')
        self.assertEqual(inspection.disposition, 'RETURN_TO_VENDOR')


class ItemBatchModelTest(TestCase):
    """Test ItemBatch model for expiry tracking."""

    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Carbide Insert',
            category=self.category,
            unit_of_measure=self.uom
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Main', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-A1',
            name='Shelf A1'
        )

    def test_batch_creation(self):
        """Test creating a batch."""
        batch = ItemBatch.objects.create(
            batch_number='BATCH-2025-001',
            item=self.item,
            location=self.location,
            quantity=Decimal('500'),
            manufacturing_date=date(2025, 1, 1),
            expiry_date=date(2026, 1, 1),
            is_quarantined=False
        )

        self.assertEqual(batch.quantity, Decimal('500'))
        self.assertFalse(batch.is_quarantined)

    def test_batch_expiry_check(self):
        """Test batch expiry checking."""
        # Expired batch
        expired_batch = ItemBatch.objects.create(
            batch_number='BATCH-EXPIRED',
            item=self.item,
            location=self.location,
            quantity=Decimal('100'),
            manufacturing_date=date(2023, 1, 1),
            expiry_date=date(2024, 1, 1)
        )

        self.assertTrue(expired_batch.is_expired())

        # Non-expired batch
        valid_batch = ItemBatch.objects.create(
            batch_number='BATCH-VALID',
            item=self.item,
            location=self.location,
            quantity=Decimal('200'),
            manufacturing_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )

        self.assertFalse(valid_batch.is_expired())


class UsedItemTrackingModelTest(TestCase):
    """Test UsedItemTracking model."""

    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='USED-001',
            name='Used Drill Motor',
            category=self.category,
            unit_of_measure=self.uom
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Main', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='USED-AREA',
            name='Used Items Area'
        )

    def test_used_item_tracking(self):
        """Test tracking used items."""
        used_item = UsedItemTracking.objects.create(
            tracking_number='USED-2025-001',
            item=self.item,
            location=self.location,
            serial_number='SN-12345',
            condition_grade='B',
            acquisition_date=date.today() - timedelta(days=30),
            acquisition_source='CUSTOMER_RETURN',
            hours_used=Decimal('150.50'),
            last_maintenance_date=date.today() - timedelta(days=10),
            next_maintenance_due=date.today() + timedelta(days=20),
            warranty_expiry=date.today() + timedelta(days=180)
        )

        self.assertEqual(used_item.condition_grade, 'B')
        self.assertEqual(used_item.acquisition_source, 'CUSTOMER_RETURN')


# ==================== Validation Utilities Tests ====================

class StockOperationValidatorTest(TestCase):
    """Test StockOperationValidator class."""

    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom,
            reorder_level=Decimal('50.00')
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Main', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-A1',
            name='Location A1'
        )

    def test_qr_code_validation_valid_item(self):
        """Test QR code validation with valid item code."""
        qr_data = f"ITEM:{self.item.item_code}|{self.item.name}|CUTTER"

        result = StockOperationValidator.validate_qr_code(qr_data, expected_type='ITEM')
        self.assertEqual(result, self.item)

    def test_qr_code_validation_wrong_type(self):
        """Test QR code validation with wrong type."""
        qr_data = f"LOCATION:{self.location.code}|{self.location.name}"

        with self.assertRaises(ValidationError) as context:
            StockOperationValidator.validate_qr_code(qr_data, expected_type='ITEM')

        self.assertIn("Wrong QR code type", str(context.exception))

    def test_qr_code_validation_nonexistent_item(self):
        """Test QR code validation with non-existent item."""
        qr_data = "ITEM:NONEXISTENT|Some Item"

        with self.assertRaises(ValidationError) as context:
            StockOperationValidator.validate_qr_code(qr_data, expected_type='ITEM')

        self.assertIn("not found", str(context.exception))

    def test_quantity_validation_too_large(self):
        """Test quantity validation with unreasonably large number."""
        with self.assertRaises(ValidationError) as context:
            StockOperationValidator.validate_quantity(15000, self.item)

        self.assertIn("unusually large", str(context.exception))

    def test_quantity_validation_too_many_decimals(self):
        """Test quantity validation with too many decimal places."""
        with self.assertRaises(ValidationError) as context:
            StockOperationValidator.validate_quantity(10.12345, self.item)

        self.assertIn("too many decimal places", str(context.exception))

    def test_quantity_validation_valid(self):
        """Test quantity validation with valid quantity."""
        result = StockOperationValidator.validate_quantity(100.5, self.item)
        self.assertEqual(result, Decimal('100.5'))

    def test_stock_availability_check(self):
        """Test checking stock availability."""
        condition = ConditionType.objects.create(code='NEW', name='New')
        ownership = OwnershipType.objects.create(code='OWN', name='Own')

        # Create stock level
        StockLevel.objects.create(
            item=self.item,
            location=self.location,
            condition_type=condition,
            ownership_type=ownership,
            quantity=Decimal('100.00')
        )

        # Check availability
        available, is_sufficient, shortage = StockOperationValidator.check_stock_availability(
            self.item, self.location, condition, ownership, Decimal('50.00')
        )

        self.assertEqual(available, Decimal('100.00'))
        self.assertTrue(is_sufficient)
        self.assertEqual(shortage, Decimal('0'))

        # Check insufficient stock
        available, is_sufficient, shortage = StockOperationValidator.check_stock_availability(
            self.item, self.location, condition, ownership, Decimal('150.00')
        )

        self.assertFalse(is_sufficient)
        self.assertEqual(shortage, Decimal('50.00'))


class ApprovalWorkflowTest(TestCase):
    """Test ApprovalWorkflow class."""

    def setUp(self):
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom,
            reorder_level=Decimal('50.00')
        )

    def test_requires_approval_large_adjustment(self):
        """Test that large adjustments require approval."""
        requires, reason = ApprovalWorkflow.requires_supervisor_approval(
            'ADJUSTMENT', 150, self.item
        )

        self.assertTrue(requires)
        self.assertIn("exceeds", reason)

    def test_requires_approval_exceeds_reorder_level(self):
        """Test that adjustments exceeding reorder level require approval."""
        requires, reason = ApprovalWorkflow.requires_supervisor_approval(
            'ADJUSTMENT', 75, self.item
        )

        self.assertTrue(requires)
        self.assertIn("reorder level", reason)

    def test_no_approval_needed_small_adjustment(self):
        """Test that small adjustments don't require approval."""
        requires, reason = ApprovalWorkflow.requires_supervisor_approval(
            'ADJUSTMENT', 25, self.item
        )

        self.assertFalse(requires)
        self.assertIsNone(reason)


class DataEntryValidatorTest(TestCase):
    """Test DataEntryValidator class."""

    def setUp(self):
        self.user = User.objects.create_user(username='operator', password='12345')
        self.category = ItemCategory.objects.create(code='CAT', name='Category')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each', is_base_unit=True)
        self.item = Item.objects.create(
            item_code='ITEM-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom
        )
        self.warehouse = Warehouse.objects.create(code='WH-01', name='Main', active=True)
        self.location = Location.objects.create(
            warehouse=self.warehouse,
            code='LOC-A1',
            name='Location A1'
        )
        self.condition = ConditionType.objects.create(code='NEW', name='New')
        self.ownership = OwnershipType.objects.create(code='OWN', name='Own')

    def test_duplicate_entry_detection(self):
        """Test detection of duplicate entries within time window."""
        # Create a recent transaction
        StockTransaction.objects.create(
            item=self.item,
            to_location=self.location,
            condition_type=self.condition,
            ownership_type=self.ownership,
            transaction_type='ADJUSTMENT',
            quantity=Decimal('50.00'),
            reference='TEST-001',
            performed_by=self.user
        )

        # Check for duplicate
        is_duplicate, similar = DataEntryValidator.check_duplicate_entry(
            self.item, self.location, 'ADJUSTMENT', Decimal('50.00')
        )

        self.assertTrue(is_duplicate)
        self.assertIsNotNone(similar)

    def test_no_duplicate_different_quantity(self):
        """Test that different quantities are not flagged as duplicates."""
        StockTransaction.objects.create(
            item=self.item,
            to_location=self.location,
            condition_type=self.condition,
            ownership_type=self.ownership,
            transaction_type='ADJUSTMENT',
            quantity=Decimal('50.00'),
            reference='TEST-002',
            performed_by=self.user
        )

        # Different quantity should not be duplicate
        is_duplicate, similar = DataEntryValidator.check_duplicate_entry(
            self.item, self.location, 'ADJUSTMENT', Decimal('100.00')
        )

        self.assertFalse(is_duplicate)
