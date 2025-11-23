# Email Notifications Setup Guide

## Overview

The logistics system includes automated email notifications for low stock alerts. This feature sends periodic alerts when items fall below their reorder levels.

## Configuration

### 1. Email Settings

Add the following to your `floor_project/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
DEFAULT_FROM_EMAIL = 'noreply@yourcompany.com'

# Low Stock Alert Recipients
LOW_STOCK_ALERT_EMAILS = [
    'inventory.manager@yourcompany.com',
    'purchasing.manager@yourcompany.com',
]
```

### 2. For Development/Testing

Use console backend to print emails to console instead of sending:

```python
# In settings.py for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

## Usage

### Manual Execution

Send low stock alerts manually:

```bash
# Send to default recipients (from settings)
python manage.py send_low_stock_alerts

# Send to specific recipients
python manage.py send_low_stock_alerts --recipients "user1@example.com,user2@example.com"

# Test mode (print email content without sending)
python manage.py send_low_stock_alerts --test
```

### Automated Scheduling

#### Option 1: Linux Cron

Add to crontab (`crontab -e`):

```cron
# Send low stock alerts every day at 8:00 AM
0 8 * * * cd /path/to/Floor-Management-System-C && /path/to/venv/bin/python manage.py send_low_stock_alerts

# Send alerts every Monday and Thursday at 9:00 AM
0 9 * * 1,4 cd /path/to/Floor-Management-System-C && /path/to/venv/bin/python manage.py send_low_stock_alerts
```

#### Option 2: Django Celery Beat (Recommended for Production)

1. Install Celery:
```bash
pip install celery django-celery-beat redis
```

2. Configure in `settings.py`:
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_BEAT_SCHEDULE = {
    'send-low-stock-alerts': {
        'task': 'inventory.tasks.send_low_stock_alerts',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
    },
}
```

3. Create `inventory/tasks.py`:
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def send_low_stock_alerts():
    call_command('send_low_stock_alerts')
```

4. Run Celery worker and beat:
```bash
celery -A floor_project worker -l info
celery -A floor_project beat -l info
```

#### Option 3: Windows Task Scheduler

1. Create a batch file `send_alerts.bat`:
```batch
cd C:\path\to\Floor-Management-System-C
C:\path\to\venv\Scripts\python.exe manage.py send_low_stock_alerts
```

2. Use Task Scheduler to run this batch file periodically

## Email Content

The system sends two types of alerts:

### Critical Items (< 25% of reorder level)
- Highlighted in red
- Requires immediate action
- Triggers urgent notification

### Warning Items (< 100% of reorder level)
- Highlighted in yellow
- Should be reviewed soon
- Standard notification

## Alert Details

Each alert includes:
- Item code and name
- Current stock level
- Reorder level
- Shortfall quantity
- Stock percentage
- Preferred supplier
- Timestamp

## Testing

Test the email system:

```bash
# Test mode - see what would be sent
python manage.py send_low_stock_alerts --test

# Send to your email only
python manage.py send_low_stock_alerts --recipients "your-email@example.com"
```

## Troubleshooting

### No emails being sent

1. Check email configuration in settings.py
2. Verify SMTP server credentials
3. Check firewall/network settings
4. Test with console backend first

### Authentication errors

- Enable "Less secure app access" for Gmail (or use App Passwords)
- For Office 365, use correct SMTP settings
- Check username/password

### Recipients not receiving emails

1. Check spam/junk folders
2. Verify email addresses in settings
3. Check email server logs
4. Test with --test flag first

## Email Provider Settings

### Gmail
```python
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### Office 365
```python
EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
```

### SendGrid
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

## Customization

### Change Alert Threshold

Edit `inventory/management/commands/send_low_stock_alerts.py`:

```python
# Change critical threshold from 25% to 10%
if stock_percentage < 10:  # Critical
    critical_items.append(item_data)
```

### Customize Email Template

Edit templates:
- HTML: `inventory/templates/inventory/emails/low_stock_alert.html`
- Text: `inventory/templates/inventory/emails/low_stock_alert.txt`

### Add More Recipients

Update settings:
```python
LOW_STOCK_ALERT_EMAILS = [
    'manager1@company.com',
    'manager2@company.com',
    'team@company.com',
]
```

## Best Practices

1. **Start with test mode** - Always test with `--test` flag first
2. **Use console backend for development** - Avoid sending real emails during testing
3. **Schedule wisely** - Send alerts during business hours (e.g., 8 AM)
4. **Monitor logs** - Check for errors in email sending
5. **Keep recipient list updated** - Review and update email addresses regularly
6. **Test periodically** - Run test sends to ensure system is working

## Security Notes

- **Never commit email passwords** to version control
- Use environment variables for sensitive data:
  ```python
  import os
  EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
  ```
- Consider using app-specific passwords instead of main account passwords
- Use SSL/TLS for secure email transmission

## See Also

- Django Email Documentation: https://docs.djangoproject.com/en/5.0/topics/email/
- Celery Documentation: https://docs.celeryproject.org/
- SendGrid Django Guide: https://sendgrid.com/docs/for-developers/sending-email/django/
