"""
HR Employment Models - Version C
Contract and shift-related models.

Separated from HREmployee to allow contract history and flexible scheduling.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


CONTRACT_TYPE_CHOICES = [
    ('PERMANENT', 'Permanent Employee'),
    ('FIXED_TERM', 'Fixed Term Contract'),
    ('TEMPORARY', 'Temporary'),
    ('PART_TIME', 'Part-Time'),
    ('INTERN', 'Internship'),
    ('CONSULTANT', 'Consultant'),
    ('CONTRACTOR', 'Contractor'),
]

SHIFT_PATTERN_CHOICES = [
    ('DAY', 'Day Shift'),
    ('NIGHT', 'Night Shift'),
    ('ROTATING', 'Rotating Shift'),
    ('FLEXIBLE', 'Flexible'),
]


class HRContract(models.Model):
    """
    Employment contract details.

    Separate from HREmployee to allow contract history tracking.
    Contains compensation details (hide-able in UI via finance panel).
    """

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='contracts',
        verbose_name="Employee"
    )

    # Contract Identification
    contract_number = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="Contract Number"
    )
    contract_type = models.CharField(
        max_length=32,
        choices=CONTRACT_TYPE_CHOICES,
        verbose_name="Contract Type"
    )

    # Duration
    start_date = models.DateField(
        verbose_name="Contract Start Date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Contract End Date",
        help_text="Leave blank for permanent contracts"
    )

    # Compensation (Finance Integration - hide in UI)
    base_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Base Salary",
        help_text="Finance: Monthly base salary"
    )
    currency = models.ForeignKey(
        'core_foundation.Currency',
        on_delete=models.PROTECT,
        verbose_name="Currency",
        help_text="Finance: Salary currency"
    )
    allowances = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Allowances",
        help_text="Finance: Additional allowances as JSON (e.g., {'housing': 1000, 'transport': 500})"
    )

    # Work Schedule
    working_hours_per_week = models.IntegerField(
        default=40,
        validators=[MinValueValidator(1)],
        verbose_name="Working Hours per Week"
    )
    shift_pattern = models.CharField(
        max_length=32,
        choices=SHIFT_PATTERN_CHOICES,
        default='DAY',
        verbose_name="Shift Pattern"
    )

    # Additional Terms
    notes = models.TextField(
        blank=True,
        verbose_name="Contract Notes"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active Contract",
        help_text="Only one contract should be active per employee at a time"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Created By"
    )

    class Meta:
        db_table = 'hr_contract'
        verbose_name = 'Employment Contract'
        verbose_name_plural = 'Employment Contracts'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['employee', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.contract_number} - {self.employee.person.full_name_en}"

    @property
    def is_permanent(self):
        """Check if this is a permanent contract."""
        return self.contract_type == 'PERMANENT'

    @property
    def total_compensation(self):
        """Calculate total monthly compensation including allowances."""
        total_allowances = sum(self.allowances.values()) if self.allowances else 0
        return self.base_salary + total_allowances


class HRShiftTemplate(models.Model):
    """
    Reusable shift definition.

    Defines standard shift patterns that can be assigned to employees.
    Simplified from old repo's complex shift configuration.
    """

    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Shift Name",
        help_text="e.g., 'Morning Shift', 'Night Shift', 'Rotating A'"
    )
    code = models.CharField(
        max_length=16,
        unique=True,
        db_index=True,
        verbose_name="Shift Code",
        help_text="Short code for the shift (e.g., 'M', 'N', 'RA')"
    )

    # Shift Hours
    start_time = models.TimeField(
        verbose_name="Shift Start Time"
    )
    end_time = models.TimeField(
        verbose_name="Shift End Time"
    )
    break_minutes = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Break Duration (minutes)"
    )

    # Classification
    is_night_shift = models.BooleanField(
        default=False,
        verbose_name="Night Shift",
        help_text="Is this a night shift (for overtime/premium calculations)?"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_shift_template'
        verbose_name = 'Shift Template'
        verbose_name_plural = 'Shift Templates'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name} ({self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')})"

    @property
    def duration_hours(self):
        """Calculate shift duration in hours (excluding breaks)."""
        from datetime import datetime, timedelta

        # Convert times to datetime for calculation
        start = datetime.combine(datetime.today(), self.start_time)
        end = datetime.combine(datetime.today(), self.end_time)

        # Handle overnight shifts
        if end < start:
            end += timedelta(days=1)

        duration = (end - start).total_seconds() / 3600  # Convert to hours
        duration -= self.break_minutes / 60  # Subtract break time

        return duration
