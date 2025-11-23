"""
HREmployee model - Employment details and work-related information.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal


class HREmployee(models.Model):
    """
    Represents an employee's employment details.
    Links a person record to their employment information.
    """

    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PROBATION', 'On Probation'),
        ('NOTICE', 'Notice Period'),
        ('SUSPENDED', 'Suspended'),
        ('TERMINATED', 'Terminated'),
        ('RESIGNED', 'Resigned'),
        ('RETIRED', 'Retired'),
    ]

    EMPLOYMENT_TYPE_CHOICES = [
        ('FULL_TIME', 'Full Time'),
        ('PART_TIME', 'Part Time'),
        ('CONTRACT', 'Contract'),
        ('TEMPORARY', 'Temporary'),
        ('INTERN', 'Intern'),
    ]

    # Link to person record
    person = models.ForeignKey(
        'HRPeople',
        on_delete=models.PROTECT,
        related_name='employments',
        help_text='Person record for this employee'
    )

    # Employee Identification
    employee_number = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique employee number'
    )
    badge_number = models.CharField(
        max_length=20,
        blank=True,
        help_text='Badge/Card number (optional)'
    )

    # User Account (Optional - for system access)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_employee',
        help_text='Linked user account for system access'
    )

    # Organizational Assignment
    department = models.ForeignKey(
        'Department',
        on_delete=models.PROTECT,
        related_name='employees',
        help_text='Department employee belongs to'
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.PROTECT,
        related_name='employees',
        help_text='Position/Job role'
    )

    # Reporting Structure
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
        help_text='Manager/Supervisor this employee reports to'
    )

    # Employment Details
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PROBATION',
        help_text='Current employment status'
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPE_CHOICES,
        default='FULL_TIME',
        help_text='Type of employment'
    )

    # Dates
    join_date = models.DateField(
        help_text='Date employee joined the organization'
    )
    probation_end_date = models.DateField(
        null=True,
        blank=True,
        help_text='End date of probation period'
    )
    confirmation_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date employee was confirmed (after probation)'
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        help_text='Date employment was terminated (if applicable)'
    )

    # Compensation
    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Basic monthly salary'
    )
    housing_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Monthly housing allowance'
    )
    transport_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Monthly transportation allowance'
    )
    other_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        default=Decimal('0.000'),
        validators=[MinValueValidator(Decimal('0.000'))],
        help_text='Other monthly allowances'
    )

    # Work Schedule
    work_hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=Decimal('8.0'),
        validators=[MinValueValidator(Decimal('0.1'))],
        help_text='Standard work hours per day'
    )
    work_days_per_week = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        help_text='Standard work days per week'
    )

    # Leave Entitlements
    annual_leave_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0)],
        help_text='Annual leave entitlement in days'
    )
    sick_leave_days = models.IntegerField(
        default=30,
        validators=[MinValueValidator(0)],
        help_text='Sick leave entitlement in days'
    )

    # Additional Information
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this employee'
    )

    # Soft Delete
    is_deleted = models.BooleanField(
        default=False,
        help_text='Soft delete flag - set to True instead of deleting'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_employees'
    )

    class Meta:
        db_table = 'hr_employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_number']
        indexes = [
            models.Index(fields=['employee_number']),
            models.Index(fields=['status', 'is_deleted']),
            models.Index(fields=['department', 'is_deleted']),
            models.Index(fields=['join_date']),
        ]

    def __str__(self):
        return f"{self.employee_number} - {self.person.get_full_name()}"

    def get_full_name(self):
        """Returns employee's full name from person record."""
        return self.person.get_full_name()

    def get_total_salary(self):
        """Calculate total monthly salary including allowances."""
        return (
            self.basic_salary +
            self.housing_allowance +
            self.transport_allowance +
            self.other_allowance
        )

    def get_service_years(self):
        """Calculate years of service."""
        from datetime import date
        end_date = self.termination_date or date.today()
        delta = end_date - self.join_date
        return delta.days / 365.25

    def is_active(self):
        """Check if employee is currently active."""
        return self.status == 'ACTIVE' and not self.is_deleted

    def is_on_probation(self):
        """Check if employee is on probation."""
        from datetime import date
        if self.status != 'PROBATION':
            return False
        if self.probation_end_date:
            return self.probation_end_date >= date.today()
        return True


class HRPhone(models.Model):
    """
    Additional phone numbers for an employee.
    """
    PHONE_TYPE_CHOICES = [
        ('MOBILE', 'Mobile'),
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    ]

    employee = models.ForeignKey(
        HREmployee,
        on_delete=models.CASCADE,
        related_name='phones'
    )
    phone_type = models.CharField(max_length=20, choices=PHONE_TYPE_CHOICES)
    phone_number = models.CharField(max_length=20)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_employee_phone'
        verbose_name = 'Employee Phone'
        verbose_name_plural = 'Employee Phones'

    def __str__(self):
        return f"{self.employee.employee_number} - {self.phone_type}: {self.phone_number}"


class HREmail(models.Model):
    """
    Additional email addresses for an employee.
    """
    EMAIL_TYPE_CHOICES = [
        ('PERSONAL', 'Personal'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    ]

    employee = models.ForeignKey(
        HREmployee,
        on_delete=models.CASCADE,
        related_name='emails'
    )
    email_type = models.CharField(max_length=20, choices=EMAIL_TYPE_CHOICES)
    email_address = models.EmailField()
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = 'hr_employee_email'
        verbose_name = 'Employee Email'
        verbose_name_plural = 'Employee Emails'

    def __str__(self):
        return f"{self.employee.employee_number} - {self.email_type}: {self.email_address}"
