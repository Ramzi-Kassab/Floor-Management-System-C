"""
HR Attendance Models - Version C
Daily attendance tracking.

Simplified from old repo: removed AttendanceSummary (calculate on-the-fly)
and complex overtime/configuration models (defer for later if needed).
"""
from django.db import models


ATTENDANCE_STATUS_CHOICES = [
    ('PRESENT', 'Present'),
    ('ABSENT', 'Absent'),
    ('LATE', 'Late'),
    ('HALF_DAY', 'Half Day'),
    ('ON_LEAVE', 'On Leave'),
]

ATTENDANCE_SOURCE_CHOICES = [
    ('MANUAL', 'Manual Entry'),
    ('IMPORTED', 'Imported from File'),
    ('WHATSAPP', 'WhatsApp Integration'),
    ('TIME_CLOCK', 'Time Clock System'),
    ('QR_SCAN', 'QR Code Scan'),
]


class AttendanceRecord(models.Model):
    """
    Daily attendance record for an employee.

    Supports multiple data sources (manual, imported, WhatsApp, QR scan).
    Tracks check-in/out times and calculates late/overtime minutes.
    """

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='attendance_records',
        verbose_name="Employee"
    )
    date = models.DateField(
        db_index=True,
        verbose_name="Attendance Date"
    )

    # Time Tracking
    check_in = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Check In Time"
    )
    check_out = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Check Out Time"
    )

    # Status
    status = models.CharField(
        max_length=16,
        choices=ATTENDANCE_STATUS_CHOICES,
        default='PRESENT',
        db_index=True,
        verbose_name="Attendance Status"
    )

    # Calculated Fields
    late_minutes = models.IntegerField(
        default=0,
        verbose_name="Late Minutes",
        help_text="Minutes late (if applicable)"
    )
    overtime_minutes = models.IntegerField(
        default=0,
        verbose_name="Overtime Minutes",
        help_text="Overtime minutes worked"
    )

    # Data Source
    source = models.CharField(
        max_length=32,
        choices=ATTENDANCE_SOURCE_CHOICES,
        default='MANUAL',
        verbose_name="Data Source"
    )

    # QR Integration (future)
    # TODO-QR: Track QR scan details for attendance
    # qr_check_in_code = models.CharField(max_length=255, blank=True)
    # qr_check_out_code = models.CharField(max_length=255, blank=True)

    # Additional Notes
    notes = models.TextField(
        blank=True,
        verbose_name="Notes"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_attendance_record'
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
        unique_together = [['employee', 'date']]
        ordering = ['-date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
        ]

    def __str__(self):
        return f"{self.employee.employee_no} - {self.date} ({self.get_status_display()})"

    @property
    def is_present(self):
        """Check if employee was present."""
        return self.status == 'PRESENT'

    @property
    def is_late(self):
        """Check if employee was late."""
        return self.late_minutes > 0 or self.status == 'LATE'

    @property
    def total_hours_worked(self):
        """Calculate total hours worked (if check-in/out recorded)."""
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            return duration.total_seconds() / 3600  # Convert to hours
        return None
