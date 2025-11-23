from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from .models import (
    Supplier, ItemCategory, UnitOfMeasure, Item,
    Warehouse, Location, ConditionType, OwnershipType,
    StockLevel, StockTransaction
)


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
