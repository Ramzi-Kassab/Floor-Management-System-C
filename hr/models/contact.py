"""
HR Contact Models - Version C
Phone numbers and email addresses for people.
"""
from django.db import models


PHONE_TYPE_CHOICES = [
    ('MOBILE', 'Mobile'),
    ('HOME', 'Home'),
    ('WORK', 'Work'),
    ('EMERGENCY', 'Emergency Contact'),
]

EMAIL_TYPE_CHOICES = [
    ('PERSONAL', 'Personal'),
    ('WORK', 'Work'),
    ('OTHER', 'Other'),
]


class HRPhone(models.Model):
    """Phone number for a person."""

    person = models.ForeignKey('HRPerson', on_delete=models.CASCADE, related_name='phones')
    phone_number = models.CharField(max_length=32)
    phone_type = models.CharField(max_length=16, choices=PHONE_TYPE_CHOICES, default='MOBILE')
    is_primary = models.BooleanField(default=False)
    is_whatsapp = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_phone'
        verbose_name = 'Phone Number'
        verbose_name_plural = 'Phone Numbers'
        ordering = ['-is_primary', 'phone_type']

    def __str__(self):
        return f"{self.phone_number} ({self.get_phone_type_display()})"


class HREmail(models.Model):
    """Email address for a person."""

    person = models.ForeignKey('HRPerson', on_delete=models.CASCADE, related_name='emails')
    email = models.EmailField()
    email_type = models.CharField(max_length=16, choices=EMAIL_TYPE_CHOICES, default='PERSONAL')
    is_primary = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_email'
        verbose_name = 'Email Address'
        verbose_name_plural = 'Email Addresses'
        ordering = ['-is_primary', 'email_type']

    def __str__(self):
        return f"{self.email} ({self.get_email_type_display()})"
