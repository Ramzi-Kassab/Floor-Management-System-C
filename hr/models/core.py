"""
HR Core Models - Version C
Foundation models for people, employees, departments, and positions.

Simplified from old repository with focus on:
- Clean separation of Person (identity) vs Employee (employment)
- Integration with core_foundation models (CostCenter)
- QR-ready structure for future badge/card integration
"""
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator


# Choices
GENDER_CHOICES = [
    ('MALE', 'Male'),
    ('FEMALE', 'Female'),
]

MARITAL_STATUS_CHOICES = [
    ('SINGLE', 'Single'),
    ('MARRIED', 'Married'),
    ('DIVORCED', 'Divorced'),
    ('WIDOWED', 'Widowed'),
]

EMPLOYMENT_STATUS_CHOICES = [
    ('ACTIVE', 'Active'),
    ('ON_PROBATION', 'On Probation'),
    ('ON_LEAVE', 'On Leave'),
    ('SUSPENDED', 'Suspended'),
    ('UNDER_NOTICE', 'Under Notice Period'),
    ('TERMINATED', 'Terminated'),
    ('RETIRED', 'Retired'),
]

POSITION_CATEGORY_CHOICES = [
    ('WORKER', 'Worker'),
    ('TECHNICIAN', 'Technician'),
    ('ENGINEER', 'Engineer'),
    ('SUPERVISOR', 'Supervisor'),
    ('MANAGER', 'Manager'),
    ('EXECUTIVE', 'Executive'),
    ('ADMINISTRATIVE', 'Administrative'),
]


class HRPerson(models.Model):
    """
    Canonical person record - pure identity, no employment data.

    Represents a person's identity that exists independently of their
    employment status. Can represent applicants, current employees, or alumni.

    Simplified from old repo: removed PublicIdMixin, SoftDelete, and
    over-engineered identity verification fields.
    """

    # Legal Names (English) - Required
    first_name_en = models.CharField(
        max_length=120,
        verbose_name="First Name (English)",
        help_text="First name in English"
    )
    middle_name_en = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Middle Name (English)",
        help_text="Middle name in English (optional)"
    )
    last_name_en = models.CharField(
        max_length=120,
        verbose_name="Last Name (English)",
        help_text="Last name in English"
    )

    # Legal Names (Arabic) - Optional
    first_name_ar = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="First Name (Arabic)",
        help_text="الاسم الأول بالعربية"
    )
    middle_name_ar = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Middle Name (Arabic)",
        help_text="الاسم الأوسط بالعربية"
    )
    last_name_ar = models.CharField(
        max_length=120,
        blank=True,
        default="",
        verbose_name="Last Name (Arabic)",
        help_text="اسم العائلة بالعربية"
    )

    # Demographics
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date of Birth"
    )
    gender = models.CharField(
        max_length=6,
        choices=GENDER_CHOICES,
        verbose_name="Gender"
    )
    nationality_iso2 = models.CharField(
        max_length=2,
        default='SA',
        verbose_name="Nationality",
        help_text="ISO 3166-1 alpha-2 country code (SA, US, IN, etc.)"
    )
    marital_status = models.CharField(
        max_length=16,
        choices=MARITAL_STATUS_CHOICES,
        blank=True,
        default="",
        verbose_name="Marital Status"
    )

    # Identity Documents
    national_id = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        verbose_name="National ID",
        help_text="National ID number (always required)"
    )
    iqama_number = models.CharField(
        max_length=10,
        blank=True,
        default="",
        db_index=True,
        verbose_name="Iqama Number",
        help_text="Iqama number (required for non-Saudi nationals)"
    )
    iqama_expiry = models.DateField(
        null=True,
        blank=True,
        verbose_name="Iqama Expiry Date"
    )

    # Photo
    photo = models.ImageField(
        upload_to='hr/people/photos/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Photo"
    )

    # QR Integration (future implementation)
    # TODO-QR: Add badge_qr_code field when QR module is implemented
    # badge_qr_code = models.CharField(max_length=255, blank=True)
    # badge_qr_generated_at = models.DateTimeField(null=True, blank=True)

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_people',
        verbose_name="Created By"
    )

    class Meta:
        db_table = 'hr_person'
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        ordering = ['last_name_en', 'first_name_en']
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['iqama_number']),
            models.Index(fields=['last_name_en', 'first_name_en']),
        ]

    def __str__(self):
        return self.full_name_en

    @property
    def full_name_en(self):
        """Full name in English."""
        parts = [self.first_name_en, self.middle_name_en, self.last_name_en]
        return ' '.join([p for p in parts if p]).strip()

    @property
    def full_name_ar(self):
        """Full name in Arabic."""
        parts = [self.first_name_ar, self.middle_name_ar, self.last_name_ar]
        return ' '.join([p for p in parts if p]).strip() or self.full_name_en

    @property
    def is_saudi(self):
        """Check if person is Saudi national."""
        return self.nationality_iso2 == 'SA'

    def clean(self):
        """Validate that non-Saudis have Iqama number."""
        from django.core.exceptions import ValidationError

        if not self.is_saudi and not self.iqama_number:
            raise ValidationError({
                'iqama_number': 'Iqama number is required for non-Saudi nationals.'
            })

        if self.is_saudi and self.iqama_number:
            raise ValidationError({
                'iqama_number': 'Saudi nationals should not have an Iqama number.'
            })


class HREmployee(models.Model):
    """
    Employment record linking a Person to the company.

    Represents the employment relationship. One Person can theoretically
    have multiple Employee records over time (rehire scenarios), though
    current implementation uses OneToOne for simplicity.

    Finance-related fields (cost_center, contract salary) are present but
    should be grouped in UI using collapsible panels.
    """

    # Core Relationships
    person = models.OneToOneField(
        HRPerson,
        on_delete=models.PROTECT,
        related_name='employment',
        verbose_name="Person"
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_employee',
        verbose_name="User Account",
        help_text="Link to Django user account for portal access"
    )

    # Employee Identification
    employee_no = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name="Employee Number",
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9-]+$',
                message='Employee number must contain only uppercase letters, numbers, and hyphens.'
            )
        ]
    )

    # Organizational Assignment
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name="Department"
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
        verbose_name="Position"
    )

    # Employment Status
    status = models.CharField(
        max_length=16,
        choices=EMPLOYMENT_STATUS_CHOICES,
        default='ACTIVE',
        db_index=True,
        verbose_name="Employment Status"
    )

    # Employment Dates
    hire_date = models.DateField(
        verbose_name="Hire Date"
    )
    probation_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Probation End Date",
        help_text="End date of probation period (if applicable)"
    )
    termination_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Termination Date"
    )
    termination_reason = models.TextField(
        blank=True,
        verbose_name="Termination Reason"
    )

    # Finance Integration (group in UI with collapsible panel)
    cost_center = models.ForeignKey(
        'core_foundation.CostCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_employees',
        verbose_name="Cost Center",
        help_text="Finance: Cost center for budgeting and reporting"
    )

    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_employees',
        verbose_name="Created By"
    )

    class Meta:
        db_table = 'hr_employee'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
        ordering = ['employee_no']
        indexes = [
            models.Index(fields=['employee_no']),
            models.Index(fields=['status']),
            models.Index(fields=['department', 'status']),
        ]

    def __str__(self):
        return f"{self.employee_no} - {self.person.full_name_en}"

    @property
    def full_name(self):
        """Convenience property for person's full name."""
        return self.person.full_name_en

    @property
    def is_active(self):
        """Check if employee is currently active."""
        return self.status == 'ACTIVE'

    @property
    def is_on_probation(self):
        """Check if employee is on probation."""
        return self.status == 'ON_PROBATION'

    def get_current_contract(self):
        """Get the currently active contract (if any)."""
        from .employment import HRContract
        return self.contracts.filter(is_active=True).first()


class Department(models.Model):
    """
    Organizational department/unit.

    Supports hierarchical structure (parent department).
    Links to CostCenter for finance integration.
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name="Department Code",
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9-]+$',
                message='Department code must contain only uppercase letters, numbers, and hyphens.'
            )
        ]
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Department Name"
    )
    name_ar = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name="Department Name (Arabic)",
        help_text="اسم القسم بالعربية"
    )

    # Hierarchy
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_departments',
        verbose_name="Parent Department"
    )

    # Finance Integration (group in UI)
    cost_center = models.ForeignKey(
        'core_foundation.CostCenter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_departments',
        verbose_name="Cost Center",
        help_text="Finance: Cost center for budgeting"
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
        db_table = 'hr_department'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def full_name(self):
        """Get full department name including parent."""
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Position(models.Model):
    """
    Job position/title in the organization.

    Defines roles that employees can be assigned to.
    Includes classification (grade level, category) for HR planning.
    """

    code = models.CharField(
        max_length=32,
        unique=True,
        db_index=True,
        verbose_name="Position Code",
        validators=[
            RegexValidator(
                regex=r'^[A-Z0-9-]+$',
                message='Position code must contain only uppercase letters, numbers, and hyphens.'
            )
        ]
    )
    title = models.CharField(
        max_length=128,
        verbose_name="Position Title"
    )
    title_ar = models.CharField(
        max_length=128,
        blank=True,
        default="",
        verbose_name="Position Title (Arabic)",
        help_text="المسمى الوظيفي بالعربية"
    )

    # Classification
    grade_level = models.CharField(
        max_length=16,
        blank=True,
        default="",
        verbose_name="Grade Level",
        help_text="e.g., 'L3', 'M2', 'S1' for internal classification"
    )
    category = models.CharField(
        max_length=32,
        choices=POSITION_CATEGORY_CHOICES,
        blank=True,
        default="",
        verbose_name="Position Category"
    )

    # Attributes
    is_supervisory = models.BooleanField(
        default=False,
        verbose_name="Supervisory Position",
        help_text="Does this position supervise other employees?"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="Active"
    )

    # Description
    description = models.TextField(
        blank=True,
        verbose_name="Position Description"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_position'
        verbose_name = 'Position'
        verbose_name_plural = 'Positions'
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.code} - {self.title}"
