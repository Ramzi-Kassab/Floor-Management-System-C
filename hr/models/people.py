"""
HRPeople model - Core person record.
Represents a person's basic information, separate from employment details.
"""
from django.db import models
from django.core.validators import RegexValidator


class HRPeople(models.Model):
    """
    Core person record containing personal information.
    Separate from employment details to handle rehires and multiple employments.
    """

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say'),
    ]

    MARITAL_STATUS_CHOICES = [
        ('SINGLE', 'Single'),
        ('MARRIED', 'Married'),
        ('DIVORCED', 'Divorced'),
        ('WIDOWED', 'Widowed'),
        ('SEPARATED', 'Separated'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A Positive'),
        ('A-', 'A Negative'),
        ('B+', 'B Positive'),
        ('B-', 'B Negative'),
        ('AB+', 'AB Positive'),
        ('AB-', 'AB Negative'),
        ('O+', 'O Positive'),
        ('O-', 'O Negative'),
    ]

    # Personal Information
    first_name = models.CharField(
        max_length=100,
        help_text='First name'
    )
    middle_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Middle name (optional)'
    )
    last_name = models.CharField(
        max_length=100,
        help_text='Last name'
    )
    full_name_arabic = models.CharField(
        max_length=200,
        blank=True,
        help_text='Full name in Arabic (optional)'
    )

    # Demographics
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Date of birth'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='U',
        help_text='Gender'
    )
    marital_status = models.CharField(
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        default='SINGLE',
        help_text='Marital status'
    )
    blood_group = models.CharField(
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True,
        help_text='Blood group (optional)'
    )

    # Identification
    national_id = models.CharField(
        max_length=50,
        unique=True,
        help_text='National ID / Civil ID number'
    )
    passport_number = models.CharField(
        max_length=50,
        blank=True,
        help_text='Passport number (optional)'
    )
    passport_expiry = models.DateField(
        null=True,
        blank=True,
        help_text='Passport expiry date (optional)'
    )

    # Contact Information (Primary)
    primary_phone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message='Enter a valid phone number with 8-15 digits'
            )
        ],
        help_text='Primary contact phone number'
    )
    primary_email = models.EmailField(
        blank=True,
        help_text='Primary email address (optional)'
    )

    # Address
    address_line1 = models.CharField(
        max_length=200,
        blank=True,
        help_text='Address line 1'
    )
    address_line2 = models.CharField(
        max_length=200,
        blank=True,
        help_text='Address line 2'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text='City'
    )
    state_province = models.CharField(
        max_length=100,
        blank=True,
        help_text='State/Province'
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text='Postal/ZIP code'
    )
    country = models.CharField(
        max_length=100,
        default='Kuwait',
        help_text='Country'
    )

    # Emergency Contact
    emergency_contact_name = models.CharField(
        max_length=200,
        blank=True,
        help_text='Emergency contact person name'
    )
    emergency_contact_relationship = models.CharField(
        max_length=50,
        blank=True,
        help_text='Relationship to emergency contact'
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{8,15}$',
                message='Enter a valid phone number with 8-15 digits'
            )
        ],
        help_text='Emergency contact phone number'
    )

    # Photo
    photo = models.ImageField(
        upload_to='hr/people/photos/',
        null=True,
        blank=True,
        help_text='Person photograph'
    )

    # Additional Notes
    notes = models.TextField(
        blank=True,
        help_text='Additional notes about this person'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_people'
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['national_id']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['primary_phone']),
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """Returns full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)

    def get_age(self):
        """Calculate age from date of birth."""
        if not self.date_of_birth:
            return None
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    def is_passport_expired(self):
        """Check if passport is expired."""
        if not self.passport_expiry:
            return None
        from datetime import date
        return self.passport_expiry < date.today()
