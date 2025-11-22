"""
HR Document Models - Version C
Employee documents (passports, licenses, certificates, etc.)
"""
from django.db import models
from django.conf import settings


class DocumentType(models.Model):
    """Type of employee document."""

    code = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    requires_renewal = models.BooleanField(default=False)
    renewal_notice_days = models.IntegerField(default=30, help_text="Notify X days before expiry")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_document_type'
        verbose_name = 'Document Type'
        verbose_name_plural = 'Document Types'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EmployeeDocument(models.Model):
    """Employee document."""

    employee = models.ForeignKey('HREmployee', on_delete=models.CASCADE, related_name='documents')
    document_type = models.ForeignKey(DocumentType, on_delete=models.PROTECT)
    document_number = models.CharField(max_length=128, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    file = models.FileField(upload_to='hr/documents/%Y/%m/', blank=True, null=True)
    notes = models.TextField(blank=True)

    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_employee_document'
        verbose_name = 'Employee Document'
        verbose_name_plural = 'Employee Documents'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.employee_no} - {self.document_type.name}"
