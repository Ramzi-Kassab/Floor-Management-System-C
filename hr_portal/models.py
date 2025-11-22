"""
HR Portal Models - Version C
Employee self-service portal models.

Lightweight models for employee requests (not leave - that's in hr.leave).
"""
from django.db import models
from django.conf import settings


REQUEST_TYPE_CHOICES = [
    ('LETTER', 'Letter Request'),
    ('DOCUMENT', 'Document Request'),
    ('DATA_UPDATE', 'Personal Data Update'),
    ('CERTIFICATE', 'Certificate Request'),
    ('OTHER', 'Other Request'),
]

REQUEST_STATUS_CHOICES = [
    ('SUBMITTED', 'Submitted'),
    ('IN_REVIEW', 'In Review'),
    ('APPROVED', 'Approved'),
    ('REJECTED', 'Rejected'),
    ('COMPLETED', 'Completed'),
]


class EmployeeRequest(models.Model):
    """
    Generic employee request (letter, document, data update, etc.)

    For leave requests, use hr.LeaveRequest instead.
    This model handles general employee service requests.
    """

    employee = models.ForeignKey(
        'hr.HREmployee',
        on_delete=models.CASCADE,
        related_name='portal_requests',
        verbose_name="Employee"
    )

    # Request Details
    request_type = models.CharField(
        max_length=32,
        choices=REQUEST_TYPE_CHOICES,
        verbose_name="Request Type"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Request Title"
    )
    description = models.TextField(
        verbose_name="Description"
    )

    # Workflow
    status = models.CharField(
        max_length=16,
        choices=REQUEST_STATUS_CHOICES,
        default='SUBMITTED',
        db_index=True,
        verbose_name="Status"
    )

    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Handled By"
    )
    handled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Handled Date"
    )
    response_notes = models.TextField(
        blank=True,
        verbose_name="HR Response Notes"
    )

    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_portal_employee_request'
        verbose_name = 'Employee Request'
        verbose_name_plural = 'Employee Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self):
        return f"{self.employee.employee_no} - {self.get_request_type_display()} ({self.title})"

    @property
    def is_pending(self):
        """Check if request is pending (submitted or in review)."""
        return self.status in ['SUBMITTED', 'IN_REVIEW']
