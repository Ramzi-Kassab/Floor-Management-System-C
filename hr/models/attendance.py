"""
Attendance tracking models.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class AttendanceRecord(models.Model):
    """Daily attendance records for employees."""
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('HALF_DAY', 'Half Day'),
        ('ON_LEAVE', 'On Leave'),
        ('WEEKEND', 'Weekend'),
        ('HOLIDAY', 'Public Holiday'),
    ]

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    date = models.DateField()

    # Clock in/out times
    clock_in = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Check-in time'
    )
    clock_out = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Check-out time'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PRESENT'
    )

    # Hours calculation
    regular_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Regular work hours'
    )
    overtime_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text='Overtime hours'
    )

    # Flags
    is_late = models.BooleanField(default=False)
    late_minutes = models.IntegerField(default=0)
    is_early_departure = models.BooleanField(default=False)
    early_departure_minutes = models.IntegerField(default=0)

    # Notes
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_attendance_records'
    )

    class Meta:
        db_table = 'hr_attendance_record'
        unique_together = ['employee', 'date']
        ordering = ['-date', 'employee']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
        ]

    def __str__(self):
        return f"{self.employee.employee_number} - {self.date} ({self.status})"

    def get_total_hours(self):
        """Calculate total hours worked."""
        return self.regular_hours + self.overtime_hours

    def is_full_day(self):
        """Check if employee worked full day."""
        return self.regular_hours >= self.employee.work_hours_per_day


class OvertimeRequest(models.Model):
    """Overtime work requests and approvals."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='overtime_requests'
    )
    date = models.DateField()
    hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    reason = models.TextField()

    # Approval
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_overtimes'
    )
    approved_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_overtime_requests'
    )

    class Meta:
        db_table = 'hr_overtime_request'
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.employee_number} - {self.date} ({self.hours}h)"
