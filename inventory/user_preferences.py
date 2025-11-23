"""
User Preferences and Settings Module
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserPreferences(models.Model):
    """
    Store user-specific preferences and settings.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')

    # Dashboard Preferences
    dashboard_view = models.CharField(
        max_length=20,
        choices=[
            ('enhanced', 'Enhanced Dashboard with Charts'),
            ('basic', 'Basic Dashboard'),
        ],
        default='enhanced',
        help_text='Default dashboard view'
    )
    items_per_page = models.IntegerField(
        default=20,
        choices=[
            (10, '10 items'),
            (20, '20 items'),
            (50, '50 items'),
            (100, '100 items'),
        ],
        help_text='Number of items to display per page in lists'
    )

    # Notification Preferences
    receive_low_stock_emails = models.BooleanField(
        default=True,
        help_text='Receive email notifications for low stock items'
    )
    low_stock_threshold = models.IntegerField(
        default=25,
        help_text='Alert when stock falls below this percentage of reorder level'
    )

    # Export Preferences
    default_export_format = models.CharField(
        max_length=10,
        choices=[
            ('excel', 'Excel (.xlsx)'),
            ('csv', 'CSV (.csv)'),
        ],
        default='excel',
        help_text='Preferred export file format'
    )

    # Display Preferences
    show_qr_codes = models.BooleanField(
        default=True,
        help_text='Show QR code buttons in item and location lists'
    )
    dark_mode = models.BooleanField(
        default=False,
        help_text='Enable dark mode theme (coming soon)'
    )

    # Language and Localization
    language = models.CharField(
        max_length=10,
        choices=[
            ('en', 'English'),
            ('ar', 'Arabic'),
        ],
        default='en',
        help_text='Preferred language'
    )
    date_format = models.CharField(
        max_length=20,
        choices=[
            ('YYYY-MM-DD', 'YYYY-MM-DD (2025-01-15)'),
            ('DD/MM/YYYY', 'DD/MM/YYYY (15/01/2025)'),
            ('MM/DD/YYYY', 'MM/DD/YYYY (01/15/2025)'),
        ],
        default='YYYY-MM-DD',
        help_text='Preferred date format'
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Automatically create preferences when a new user is created."""
    if created:
        UserPreferences.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    """Save preferences when user is saved."""
    if not hasattr(instance, 'preferences'):
        UserPreferences.objects.create(user=instance)
    else:
        instance.preferences.save()
