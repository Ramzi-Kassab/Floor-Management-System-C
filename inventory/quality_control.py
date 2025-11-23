"""
Quality Control and Item Lifecycle Management
Handles defective items, expiry tracking, used items, and quality inspections.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta


class QualityInspection(models.Model):
    """
    Quality inspection record for items received or in inventory.
    Determines if items are acceptable, need rework, or should be rejected.
    """

    INSPECTION_TYPE_CHOICES = [
        ('RECEIVING', 'Receiving Inspection'),
        ('IN_PROCESS', 'In-Process Inspection'),
        ('FINAL', 'Final Inspection'),
        ('PERIODIC', 'Periodic Stock Inspection'),
        ('CUSTOMER_RETURN', 'Customer Return Inspection'),
    ]

    INSPECTION_RESULT_CHOICES = [
        ('PASS', 'Pass - Accept'),
        ('CONDITIONAL', 'Conditional Pass - Minor Issues'),
        ('REWORK', 'Rework Required'),
        ('REJECT', 'Reject - Return to Vendor'),
        ('SCRAP', 'Scrap - Unusable'),
    ]

    inspection_number = models.CharField(max_length=50, unique=True)
    inspection_type = models.CharField(max_length=20, choices=INSPECTION_TYPE_CHOICES)
    inspection_date = models.DateField(default=date.today)

    # Related to GRN if receiving inspection
    goods_receipt_line = models.ForeignKey(
        'purchasing.GoodsReceiptLine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_inspections'
    )

    # Or related to stock if periodic inspection
    item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        related_name='quality_inspections'
    )
    batch_number = models.CharField(max_length=100, blank=True, help_text="Batch/Lot number")
    quantity_inspected = models.DecimalField(max_digits=12, decimal_places=2)

    # Inspection results
    inspection_result = models.CharField(max_length=20, choices=INSPECTION_RESULT_CHOICES)
    quantity_accepted = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_rejected = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity_for_rework = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Defect tracking
    defect_description = models.TextField(blank=True, help_text="Description of defects found")
    defect_category = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Dimensional, Visual, Functional, Material"
    )
    defect_severity = models.CharField(
        max_length=20,
        choices=[
            ('CRITICAL', 'Critical - Safety/Function Impact'),
            ('MAJOR', 'Major - Performance Impact'),
            ('MINOR', 'Minor - Aesthetic Only'),
        ],
        blank=True
    )

    # Inspector details
    inspected_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='quality_inspections'
    )
    inspection_notes = models.TextField(blank=True)

    # Photos/attachments
    photo_url = models.URLField(blank=True, help_text="URL to defect photos")

    # Actions taken
    action_taken = models.TextField(
        blank=True,
        help_text="Actions taken based on inspection result"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-inspection_date', '-inspection_number']
        verbose_name = 'Quality Inspection'
        verbose_name_plural = 'Quality Inspections'

    def __str__(self):
        return f"{self.inspection_number} - {self.item.item_code} - {self.get_inspection_result_display()}"

    @property
    def pass_rate(self):
        """Calculate inspection pass rate percentage."""
        if self.quantity_inspected > 0:
            return (self.quantity_accepted / self.quantity_inspected) * 100
        return 0


class ItemBatch(models.Model):
    """
    Track batches/lots of items with expiry dates and manufacturing details.
    Critical for managing expired items and FEFO (First Expired First Out).
    """

    batch_number = models.CharField(max_length=100, unique=True)
    item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        related_name='batches'
    )

    # Manufacturing details
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Use for items with expiration (chemicals, consumables, etc.)"
    )
    shelf_life_days = models.IntegerField(
        null=True,
        blank=True,
        help_text="Shelf life in days from manufacturing date"
    )

    # Supplier batch info
    supplier_batch_number = models.CharField(max_length=100, blank=True)
    supplier = models.ForeignKey(
        'Supplier',
        on_delete=models.PROTECT,
        related_name='batches',
        null=True,
        blank=True
    )

    # Certificates and documentation
    certificate_number = models.CharField(max_length=100, blank=True, help_text="Quality certificate number")
    certificate_url = models.URLField(blank=True, help_text="URL to certificate document")

    # Status
    is_quarantined = models.BooleanField(
        default=False,
        help_text="True if batch is under quarantine/inspection"
    )
    is_expired = models.BooleanField(default=False, help_text="Manually marked as expired")
    is_recalled = models.BooleanField(default=False, help_text="Supplier recall")
    recall_reason = models.TextField(blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['expiry_date', 'batch_number']
        verbose_name = 'Item Batch'
        verbose_name_plural = 'Item Batches'

    def __str__(self):
        return f"{self.batch_number} - {self.item.item_code}"

    @property
    def days_until_expiry(self):
        """Calculate days remaining until expiry."""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None

    @property
    def is_near_expiry(self):
        """Check if batch is near expiry (within 30 days)."""
        days = self.days_until_expiry
        if days is not None:
            return 0 <= days <= 30
        return False

    @property
    def has_expired(self):
        """Check if batch has expired."""
        if self.is_expired:
            return True
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    def get_stock_in_batch(self):
        """Get current stock quantity for this batch."""
        from .models import StockLevel
        return StockLevel.objects.filter(
            item=self.item,
            batch_number=self.batch_number
        ).aggregate(models.Sum('quantity'))['quantity__sum'] or Decimal('0')


class DefectiveItemDisposition(models.Model):
    """
    Track disposition of defective items.
    Records what happens to items that fail inspection.
    """

    DISPOSITION_CHOICES = [
        ('RETURN_VENDOR', 'Return to Vendor'),
        ('REWORK', 'Send for Rework/Repair'),
        ('SCRAP', 'Scrap - Destroy'),
        ('DOWNGRADE', 'Downgrade - Sell as Second Grade'),
        ('USE_AS_IS', 'Use As-Is (with concession)'),
        ('HOLD', 'Hold for Further Review'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending Disposition'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    disposition_number = models.CharField(max_length=50, unique=True)
    quality_inspection = models.ForeignKey(
        QualityInspection,
        on_delete=models.PROTECT,
        related_name='dispositions'
    )

    disposition_type = models.CharField(max_length=20, choices=DISPOSITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    # Financial impact
    estimated_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Estimated financial loss"
    )
    recovery_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Value recovered (if sold as scrap/downgrade)"
    )

    # Disposition details
    disposed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='dispositions'
    )
    disposition_date = models.DateField()
    completion_date = models.DateField(null=True, blank=True)

    # For rework/repair
    rework_location = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rework_items',
        help_text="Location where rework is performed"
    )
    rework_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    # For returns
    return_authorization = models.CharField(
        max_length=100,
        blank=True,
        help_text="RMA or return authorization number"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-disposition_date', '-disposition_number']
        verbose_name = 'Defective Item Disposition'
        verbose_name_plural = 'Defective Item Dispositions'

    def __str__(self):
        return f"{self.disposition_number} - {self.get_disposition_type_display()}"


class UsedItemTracking(models.Model):
    """
    Track history and condition of used/second-hand items.
    Maintains lifecycle information for items that are reused.
    """

    CONDITION_GRADE_CHOICES = [
        ('A', 'Grade A - Excellent (Like New)'),
        ('B', 'Grade B - Good (Minor Wear)'),
        ('C', 'Grade C - Fair (Visible Wear)'),
        ('D', 'Grade D - Poor (Significant Wear)'),
        ('R', 'Refurbished'),
    ]

    item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        related_name='used_tracking'
    )

    # Item identification
    serial_number = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique serial number for this specific item"
    )

    # Purchase/acquisition
    original_purchase_date = models.DateField(null=True, blank=True)
    original_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    current_book_value = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Current depreciated value"
    )

    # Condition assessment
    condition_grade = models.CharField(max_length=1, choices=CONDITION_GRADE_CHOICES)
    last_inspection_date = models.DateField(null=True, blank=True)
    next_inspection_due = models.DateField(null=True, blank=True)

    # Usage tracking
    hours_used = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total hours of usage (for equipment)"
    )
    cycles_used = models.IntegerField(
        default=0,
        help_text="Number of usage cycles (for tools)"
    )

    # Maintenance history
    last_maintenance_date = models.DateField(null=True, blank=True)
    next_maintenance_due = models.DateField(null=True, blank=True)
    maintenance_notes = models.TextField(blank=True)

    # Warranty
    warranty_expiry = models.DateField(null=True, blank=True)
    warranty_terms = models.TextField(blank=True)

    # Current status
    is_serviceable = models.BooleanField(
        default=True,
        help_text="Item is in working condition"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Item is available for use"
    )
    current_user = models.CharField(
        max_length=200,
        blank=True,
        help_text="Person/department currently using the item"
    )

    # Photos and documentation
    photo_url = models.URLField(blank=True)
    documentation_url = models.URLField(blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_inspection_date', 'serial_number']
        verbose_name = 'Used Item Tracking'
        verbose_name_plural = 'Used Item Tracking'

    def __str__(self):
        return f"{self.item.item_code} - S/N: {self.serial_number} - Grade {self.condition_grade}"

    @property
    def is_under_warranty(self):
        """Check if item is still under warranty."""
        if self.warranty_expiry:
            return date.today() <= self.warranty_expiry
        return False

    @property
    def needs_maintenance(self):
        """Check if maintenance is due."""
        if self.next_maintenance_due:
            return date.today() >= self.next_maintenance_due
        return False


class ExpiredItemAction(models.Model):
    """
    Track actions taken for expired items.
    Records disposal, write-off, or other handling of expired inventory.
    """

    ACTION_TYPE_CHOICES = [
        ('DISPOSE', 'Dispose/Destroy'),
        ('WRITE_OFF', 'Write Off'),
        ('RETURN_VENDOR', 'Return to Vendor'),
        ('DONATE', 'Donate'),
        ('SELL_DISCOUNT', 'Sell at Discount'),
        ('EXTEND_LIFE', 'Extend Shelf Life (with approval)'),
    ]

    action_number = models.CharField(max_length=50, unique=True)
    batch = models.ForeignKey(
        ItemBatch,
        on_delete=models.PROTECT,
        related_name='expiry_actions'
    )

    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICES)
    action_date = models.DateField()
    quantity = models.DecimalField(max_digits=12, decimal_places=2)

    # Financial details
    book_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Book value of expired items"
    )
    recovery_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Amount recovered (if any)"
    )
    loss_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Net loss amount"
    )

    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='expiry_approvals',
        null=True,
        blank=True
    )
    approval_date = models.DateField(null=True, blank=True)

    # Execution
    executed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='expiry_actions'
    )

    # Documentation
    disposal_certificate = models.CharField(
        max_length=100,
        blank=True,
        help_text="Certificate number for disposal"
    )
    documentation_url = models.URLField(blank=True)

    reason = models.TextField(help_text="Reason for expiry/action taken")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-action_date', '-action_number']
        verbose_name = 'Expired Item Action'
        verbose_name_plural = 'Expired Item Actions'

    def __str__(self):
        return f"{self.action_number} - {self.batch.batch_number} - {self.get_action_type_display()}"


# Add to inventory/models.py - extend StockLevel model
class StockLevelExtended(models.Model):
    """
    Extended stock level information (if needed to add to existing StockLevel).
    This would be a one-to-one relationship with StockLevel.
    """

    # Link to main StockLevel
    stock_level = models.OneToOneField(
        'StockLevel',
        on_delete=models.CASCADE,
        related_name='extended_info'
    )

    # Batch tracking
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    # Quality status
    quality_status = models.CharField(
        max_length=20,
        choices=[
            ('APPROVED', 'Quality Approved'),
            ('QUARANTINE', 'Under Quarantine'),
            ('REJECTED', 'Quality Rejected'),
            ('REWORK', 'In Rework'),
        ],
        default='APPROVED'
    )

    # Usage restrictions
    is_restricted = models.BooleanField(
        default=False,
        help_text="Restricted use (e.g., for specific project only)"
    )
    restriction_reason = models.TextField(blank=True)

    # Alerts
    near_expiry_alert_sent = models.BooleanField(default=False)
    last_alert_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Stock Level Extended Info'
        verbose_name_plural = 'Stock Level Extended Info'
