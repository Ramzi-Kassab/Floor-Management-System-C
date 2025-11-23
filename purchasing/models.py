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
