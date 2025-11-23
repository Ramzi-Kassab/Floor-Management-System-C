"""
Employee document management models.
"""
from django.db import models
from django.conf import settings


class DocumentType(models.Model):
    """Types of documents for employees."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Requirements
    is_mandatory = models.BooleanField(default=False)
    has_expiry = models.BooleanField(
        default=False,
        help_text='Whether this document type has an expiry date'
    )
    renewal_notice_days = models.IntegerField(
        default=30,
        help_text='Days before expiry to send renewal notice'
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_document_type'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EmployeeDocument(models.Model):
    """Documents associated with employees."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Verification'),
        ('VERIFIED', 'Verified'),
        ('REJECTED', 'Rejected'),
        ('EXPIRED', 'Expired'),
    ]

    employee = models.ForeignKey(
        'HREmployee',
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT
    )

    # Document details
    document_number = models.CharField(
        max_length=100,
        blank=True,
        help_text='Document identification number'
    )
    issue_date = models.DateField(
        null=True,
        blank=True
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text='Expiry date (if applicable)'
    )

    # File upload
    document_file = models.FileField(
        upload_to='hr/documents/%Y/%m/',
        help_text='Uploaded document file'
    )

    # Verification
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_date = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(blank=True)

    # Additional information
    notes = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_employee_documents'
    )

    class Meta:
        db_table = 'hr_employee_document'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'document_type']),
            models.Index(fields=['expiry_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.employee.employee_number} - {self.document_type.code}"

    def is_expired(self):
        """Check if document is expired."""
        if not self.expiry_date:
            return False
        from datetime import date
        return self.expiry_date < date.today()

    def days_until_expiry(self):
        """Calculate days until document expires."""
        if not self.expiry_date:
            return None
        from datetime import date
        delta = self.expiry_date - date.today()
        return delta.days

    def needs_renewal(self):
        """Check if document needs renewal soon."""
        if not self.expiry_date or not self.document_type.has_expiry:
            return False
        days_left = self.days_until_expiry()
        if days_left is None:
            return False
        return days_left <= self.document_type.renewal_notice_days
