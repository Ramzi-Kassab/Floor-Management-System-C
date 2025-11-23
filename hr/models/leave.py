"""
Leave management models.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class LeaveType(models.Model):
    """Types of leave available."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_paid = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    # Limits
    max_days_per_request = models.IntegerField(
        null=True,
        blank=True,
        help_text='Maximum days allowed per request (null=unlimited)'
    )
    min_advance_notice_days = models.IntegerField(
        default=0,
        help_text='Minimum days notice required before leave'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_leave_type'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class LeavePolicy(models.Model):
    """Leave policies defining entitlements."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='policies'
    )

    # Entitlement
    days_per_year = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.0'))]
    )
    accrual_method = models.CharField(
        max_length=20,
        choices=[
            ('ANNUAL', 'Annual Grant'),
            ('MONTHLY', 'Monthly Accrual'),
            ('DAILY', 'Daily Accrual'),
        ],
        default='ANNUAL'
    )

    # Carry forward
    allow_carryforward = models.BooleanField(default=False)
    max_carryforward_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0')
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_leave_policy'
        verbose_name_plural = 'Leave Policies'

    def __str__(self):
        return f"{self.name} ({self.leave_type.code})"


class LeaveBalance(models.Model):
    """Employee leave balance tracking."""
    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE
    )
    year = models.IntegerField()

    # Balance tracking
    entitled_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0')
    )
    used_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0')
    )
    pending_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0'),
        help_text='Days in pending requests'
    )
    carried_forward = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal('0.0')
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_leave_balance'
        unique_together = ['employee', 'leave_type', 'year']
        ordering = ['-year', 'employee']

    def __str__(self):
        return f"{self.employee.employee_number} - {self.leave_type.code} ({self.year})"

    def get_available_days(self):
        """Calculate available leave days."""
        return self.entitled_days + self.carried_forward - self.used_days - self.pending_days


class LeaveRequest(models.Model):
    """Employee leave requests."""
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    ]

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT
    )

    # Request details
    start_date = models.DateField()
    end_date = models.DateField()
    number_of_days = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal('0.5'))]
    )
    reason = models.TextField(help_text='Reason for leave request')

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DRAFT'
    )
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_leave_requests'
    )

    class Meta:
        db_table = 'hr_leave_request'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee.employee_number} - {self.leave_type.code} ({self.start_date} to {self.end_date})"

    def is_approved(self):
        return self.status == 'APPROVED'

    def is_pending(self):
        return self.status == 'PENDING'

    def can_cancel(self):
        """Check if leave request can be cancelled."""
        return self.status in ['DRAFT', 'PENDING', 'APPROVED']
