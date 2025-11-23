"""
Employee qualification and skill management models.
"""
from django.db import models
from django.conf import settings


class QualificationLevel(models.Model):
    """Educational/Professional qualification levels."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level = models.IntegerField(
        help_text='Qualification level (higher number = higher qualification)'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_qualification_level'
        ordering = ['-level']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EmployeeQualification(models.Model):
    """Employee educational qualifications and certifications."""
    QUALIFICATION_TYPE_CHOICES = [
        ('EDUCATION', 'Educational Degree'),
        ('CERTIFICATION', 'Professional Certification'),
        ('TRAINING', 'Training Certificate'),
        ('LICENSE', 'License/Permit'),
        ('OTHER', 'Other'),
    ]

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='qualifications'
    )
    qualification_level = models.ForeignKey(
        QualificationLevel,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    # Qualification details
    qualification_type = models.CharField(
        max_length=20,
        choices=QUALIFICATION_TYPE_CHOICES,
        default='EDUCATION'
    )
    title = models.CharField(
        max_length=200,
        help_text='Qualification title/name'
    )
    institution = models.CharField(
        max_length=200,
        help_text='Issuing institution/organization'
    )
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        help_text='Field/Major (for educational degrees)'
    )

    # Dates
    start_date = models.DateField(null=True, blank=True)
    completion_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expiry date (for certifications/licenses)'
    )

    # Verification
    certificate_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Certificate/Degree number'
    )
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_qualifications'
    )
    verified_date = models.DateTimeField(null=True, blank=True)

    # Supporting documents
    document_file = models.FileField(
        upload_to='hr/qualifications/%Y/%m/',
        null=True,
        blank=True,
        help_text='Uploaded certificate/degree file'
    )

    # Additional information
    grade_gpa = models.CharField(
        max_length=50,
        blank=True,
        help_text='Grade/GPA achieved'
    )
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_qualifications'
    )

    class Meta:
        db_table = 'hr_employee_qualification'
        ordering = ['-completion_date']
        indexes = [
            models.Index(fields=['employee', 'qualification_type']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.employee.employee_number} - {self.title}"

    def is_expired(self):
        """Check if qualification is expired."""
        if not self.expiry_date:
            return False
        from datetime import date
        return self.expiry_date < date.today()

    def days_until_expiry(self):
        """Calculate days until qualification expires."""
        if not self.expiry_date:
            return None
        from datetime import date
        delta = self.expiry_date - date.today()
        return delta.days
