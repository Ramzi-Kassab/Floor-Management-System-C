"""
HR Leave Models - Version C
Leave management system.

Simplified from old repo: removed LeaveBalance and LeavePolicy models.
Leave balance is calculated on-the-fly from approved requests.
"""
from django.db import models
from django.conf import settings


REQUEST_STATUS_CHOICES = [
    ('DRAFT', 'Draft'),
    ('SUBMITTED', 'Submitted'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('CANCELLED', 'Cancelled'),
]


class LeaveType(models.Model):
    """
    Type of leave (Annual, Sick, Emergency, etc.)

    Merged functionality from old repo's LeaveType and LeavePolicy models.
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name="Leave Type Code"
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Leave Type Name"
    )
    name_ar = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name="Leave Type Name (Arabic)"
    )

    # Leave Policy Settings
    is_paid = models.BooleanField(
        default=True,
        verbose_name="Paid Leave",
        help_text="Is this a paid leave type?"
    )
    requires_approval = models.BooleanField(
        default=True,
        verbose_name="Requires Approval",
        help_text="Does this leave type require manager approval?"
    )
    max_days_per_year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="Max Days Per Year",
        help_text="Maximum days allowed per year (leave blank for unlimited)"
    )
    min_notice_days = models.IntegerField(
        default=0,
        verbose_name="Minimum Notice Days",
        help_text="Minimum days of advance notice required"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active"
    )

    # Description
    description = models.TextField(
        blank=True,
        verbose_name="Description"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_leave_type'
        verbose_name = 'Leave Type'
        verbose_name_plural = 'Leave Types'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class LeaveRequest(models.Model):
    """
    Employee leave request.

    Supports approval workflow and notification integration.
    """

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='leave_requests',
        verbose_name="Employee"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.PROTECT,
        related_name='requests',
        verbose_name="Leave Type"
    )

    # Leave Period
    start_date = models.DateField(
        verbose_name="Start Date"
    )
    end_date = models.DateField(
        verbose_name="End Date"
    )
    days_count = models.IntegerField(
        verbose_name="Number of Days",
        help_text="Total number of leave days (auto-calculated)"
    )

    # Request Details
    reason = models.TextField(
        blank=True,
        verbose_name="Reason",
        help_text="Reason for leave request"
    )

    # Approval Workflow
    status = models.CharField(
        max_length=16,
        choices=REQUEST_STATUS_CHOICES,
        default='DRAFT',
        db_index=True,
        verbose_name="Status"
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Approved By"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Approval Date"
    )
    rejection_reason = models.TextField(
        blank=True,
        verbose_name="Rejection Reason"
    )

    # Integration with core_foundation approval system
    approval_type = models.ForeignKey(
        'core_foundation.ApprovalType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Approval Type",
        help_text="Optional: Link to approval workflow from core_foundation"
    )

    # QR Integration (future)
    # TODO-QR: Add QR code for approval via mobile scan
    # approval_qr_code = models.CharField(max_length=255, blank=True)

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Submitted By"
    )

    class Meta:
        db_table = 'hr_leave_request'
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['leave_type', 'status']),
        ]

    def __str__(self):
        return f"{self.employee.employee_no} - {self.leave_type.code} ({self.start_date} to {self.end_date})"

    @property
    def is_pending(self):
        """Check if request is pending approval."""
        return self.status in ['DRAFT', 'SUBMITTED']

    @property
    def is_approved(self):
        """Check if request is approved."""
        return self.status == 'APPROVED'

    def save(self, *args, **kwargs):
        """Auto-calculate days_count if not set."""
        if not self.days_count:
            self.days_count = (self.end_date - self.start_date).days + 1
        super().save(*args, **kwargs)

    def approve(self, approved_by_user):
        """
        Approve the leave request.

        Args:
            approved_by_user: User approving the request

        Triggers Notification (from core_foundation) to employee.
        """
        from django.utils import timezone

        self.status = 'APPROVED'
        self.approved_by = approved_by_user
        self.approved_at = timezone.now()
        self.save()

        # TODO: Send notification to employee
        # from core_foundation.models import Notification
        # Notification.objects.create(
        #     user=self.employee.user,
        #     title=f"Leave Request Approved",
        #     message=f"Your {self.leave_type.name} request for {self.days_count} days has been approved.",
        #     priority='medium',
        #     content_object=self
        # )

    def reject(self, rejected_by_user, reason=""):
        """
        Reject the leave request.

        Args:
            rejected_by_user: User rejecting the request
            reason: Rejection reason
        """
        from django.utils import timezone

        self.status = 'REJECTED'
        self.approved_by = rejected_by_user
        self.approved_at = timezone.now()
        self.rejection_reason = reason
        self.save()

        # TODO: Send notification to employee
        # Notification.objects.create(
        #     user=self.employee.user,
        #     title=f"Leave Request Rejected",
        #     message=f"Your {self.leave_type.name} request has been rejected. Reason: {reason}",
        #     priority='high',
        #     content_object=self
        # )
