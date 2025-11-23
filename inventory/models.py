from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Supplier(models.Model):
    """Represents a supplier of materials and items."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique supplier code")
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100, blank=True)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True)
    payment_terms = models.CharField(max_length=200, blank=True, help_text="e.g., Net 30, Net 60")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'

    def __str__(self):
        return f"{self.code} - {self.name}"


class ItemCategory(models.Model):
    """Hierarchical category for items."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique category code")
    name = models.CharField(max_length=200, help_text="e.g., Cutters, Matrix Powder, Steel Forgings")
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subcategories',
        help_text="Parent category for hierarchical structure"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Item Category'
        verbose_name_plural = 'Item Categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.code} > {self.code} - {self.name}"
        return f"{self.code} - {self.name}"


class UnitOfMeasure(models.Model):
    """Unit of measure for items (EA, KG, L, M, etc.)."""
    code = models.CharField(max_length=20, unique=True, help_text="e.g., EA, KG, L, M")
    name = models.CharField(max_length=100, help_text="e.g., Each, Kilogram, Liter, Meter")
    is_base_unit = models.BooleanField(default=False, help_text="Is this the base unit for conversions?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Item(models.Model):
    """Master data for inventory items."""

    ITEM_TYPE_CHOICES = [
        ('CUTTER', 'PDC Cutter'),
        ('MATRIX_POWDER', 'Matrix Powder'),
        ('BINDER', 'Binder'),
        ('STEEL_BODY', 'Steel Body/Forging'),
        ('JV_PARTIAL_BODY', 'JV Semi-finished Body'),
        ('UPPER_SECTION', 'Upper Section (API Connection)'),
        ('HARDFACING_POWDER', 'Hardfacing Powder'),
        ('FLUX', 'Flux'),
        ('BRAZING_ALLOY', 'Brazing Alloy'),
        ('CONSUMABLE', 'Consumable'),
        ('TOOL', 'Tool'),
        ('SPARE_PART', 'Spare Part'),
        ('GAS', 'Gas'),
        ('OTHER', 'Other'),
    ]

    item_code = models.CharField(max_length=100, unique=True, help_text="Unique item code")
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        ItemCategory,
        on_delete=models.PROTECT,
        related_name='items',
        help_text="Item category"
    )
    unit_of_measure = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='items',
        help_text="Primary unit of measure"
    )
    description = models.TextField(blank=True)
    item_type = models.CharField(
        max_length=50,
        choices=ITEM_TYPE_CHOICES,
        default='OTHER',
        help_text="Type of item"
    )
    active = models.BooleanField(default=True)
    reorder_level = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Minimum stock level before reorder"
    )
    preferred_supplier = models.ForeignKey(
        Supplier,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='preferred_items',
        help_text="Preferred supplier for this item"
    )
    # Future QR code support - don't add QR field now, but design allows it
    external_reference = models.CharField(max_length=100, blank=True, help_text="External ERP reference")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_code']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return f"{self.item_code} - {self.name}"


class Warehouse(models.Model):
    """Physical warehouse location."""
    code = models.CharField(max_length=50, unique=True, help_text="Unique warehouse code")
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'

    def __str__(self):
        return f"{self.code} - {self.name}"


class Location(models.Model):
    """Specific storage location within a warehouse."""
    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name='locations',
        help_text="Parent warehouse"
    )
    code = models.CharField(max_length=50, help_text="e.g., CUTTER-RACK-01, POWDER-SILO-1")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_virtual = models.BooleanField(
        default=False,
        help_text="Virtual location for adjustments, scrap, etc."
    )
    # Future QR code support
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['warehouse__code', 'code']
        unique_together = [['warehouse', 'code']]
        verbose_name = 'Location'
        verbose_name_plural = 'Locations'

    def __str__(self):
        return f"{self.warehouse.code} > {self.code} - {self.name}"


class ConditionType(models.Model):
    """Condition of stock items (NEW, USED, REPAIRABLE, SCRAP, etc.)."""
    code = models.CharField(max_length=50, unique=True, help_text="e.g., NEW, USED, REPAIRABLE, SCRAP")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Condition Type'
        verbose_name_plural = 'Condition Types'

    def __str__(self):
        return f"{self.code} - {self.name}"


class OwnershipType(models.Model):
    """Ownership type of stock (OWN, CUSTOMER, CONSIGNMENT, JV_OWNED, etc.)."""
    code = models.CharField(max_length=50, unique=True, help_text="e.g., OWN, CUSTOMER, CONSIGNMENT, JV_OWNED")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'Ownership Type'
        verbose_name_plural = 'Ownership Types'

    def __str__(self):
        return f"{self.code} - {self.name}"


class StockLevel(models.Model):
    """Current stock level for an item at a specific location with condition and ownership."""
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='stock_levels'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='stock_levels'
    )
    condition_type = models.ForeignKey(
        ConditionType,
        on_delete=models.PROTECT,
        related_name='stock_levels'
    )
    ownership_type = models.ForeignKey(
        OwnershipType,
        on_delete=models.PROTECT,
        related_name='stock_levels'
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['item', 'location', 'condition_type', 'ownership_type']]
        verbose_name = 'Stock Level'
        verbose_name_plural = 'Stock Levels'
        indexes = [
            models.Index(fields=['item', 'location']),
            models.Index(fields=['item']),
        ]

    def __str__(self):
        return f"{self.item.item_code} @ {self.location.code}: {self.quantity} {self.item.unit_of_measure.code}"


class StockTransaction(models.Model):
    """Record of stock movements and transactions."""

    TRANSACTION_TYPE_CHOICES = [
        ('PURCHASE_RECEIPT', 'Purchase Receipt'),
        ('ISSUE_TO_PRODUCTION', 'Issue to Production'),
        ('RETURN_FROM_PRODUCTION', 'Return from Production'),
        ('TRANSFER', 'Transfer'),
        ('ADJUSTMENT', 'Adjustment'),
        ('SCRAP', 'Scrap'),
        ('INITIAL_STOCK', 'Initial Stock'),
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    from_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='transactions_from',
        help_text="Source location (null for receipts)"
    )
    to_location = models.ForeignKey(
        Location,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='transactions_to',
        help_text="Destination location (null for issues)"
    )
    condition_type = models.ForeignKey(
        ConditionType,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    ownership_type = models.ForeignKey(
        OwnershipType,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="Type of stock transaction"
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity moved"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference number (PO, JobCard, WO, etc.)"
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='stock_transactions'
    )
    notes = models.TextField(blank=True)
    external_reference = models.CharField(max_length=100, blank=True, help_text="External ERP reference")

    class Meta:
        ordering = ['-performed_at']
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'
        indexes = [
            models.Index(fields=['item', '-performed_at']),
            models.Index(fields=['transaction_type', '-performed_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type}: {self.item.item_code} - {self.quantity} ({self.performed_at.strftime('%Y-%m-%d %H:%M')})"
