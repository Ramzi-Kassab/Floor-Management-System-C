"""
Management command to send low stock email alerts.
Run this periodically (e.g., daily via cron) to notify users about low stock items.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models import Sum, F
from inventory.models import Item
from datetime import datetime


class Command(BaseCommand):
    help = 'Send email alerts for low stock items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipients',
            type=str,
            help='Comma-separated list of recipient email addresses',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode - print email content instead of sending',
        )

    def handle(self, *args, **options):
        # Get low stock items
        low_stock_items = Item.objects.filter(active=True).annotate(
            total_stock=Sum('stock_levels__quantity')
        ).filter(
            total_stock__lt=F('reorder_level')
        ).select_related('category', 'unit_of_measure', 'preferred_supplier')

        if not low_stock_items.exists():
            self.stdout.write(self.style.SUCCESS('No low stock items found.'))
            return

        # Calculate urgency levels
        critical_items = []
        warning_items = []

        for item in low_stock_items:
            stock_percentage = (item.total_stock / item.reorder_level * 100) if item.reorder_level > 0 else 0

            item_data = {
                'item': item,
                'total_stock': item.total_stock or 0,
                'stock_percentage': stock_percentage,
                'shortfall': item.reorder_level - (item.total_stock or 0)
            }

            if stock_percentage < 25:  # Critical: less than 25% of reorder level
                critical_items.append(item_data)
            else:  # Warning: 25-100% of reorder level
                warning_items.append(item_data)

        # Prepare email context
        context = {
            'critical_items': critical_items,
            'warning_items': warning_items,
            'total_low_stock': len(low_stock_items),
            'check_date': datetime.now(),
        }

        # Render email templates
        html_content = render_to_string('inventory/emails/low_stock_alert.html', context)
        text_content = render_to_string('inventory/emails/low_stock_alert.txt', context)

        # Get recipients
        if options['recipients']:
            recipients = [email.strip() for email in options['recipients'].split(',')]
        else:
            # Default recipients from settings
            recipients = getattr(settings, 'LOW_STOCK_ALERT_EMAILS', [])

        if not recipients:
            self.stdout.write(
                self.style.WARNING(
                    'No recipients specified. Use --recipients or set LOW_STOCK_ALERT_EMAILS in settings.'
                )
            )
            return

        # Test mode
        if options['test']:
            self.stdout.write(self.style.SUCCESS('=== TEST MODE ==='))
            self.stdout.write(f'Recipients: {", ".join(recipients)}')
            self.stdout.write(f'Subject: Low Stock Alert - {len(low_stock_items)} Items')
            self.stdout.write('\n=== TEXT CONTENT ===')
            self.stdout.write(text_content)
            self.stdout.write('\n=== HTML CONTENT ===')
            self.stdout.write(html_content)
            return

        # Send email
        try:
            email = EmailMultiAlternatives(
                subject=f'Low Stock Alert - {len(low_stock_items)} Items Need Attention',
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=recipients,
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully sent low stock alert to {len(recipients)} recipient(s). '
                    f'{len(critical_items)} critical, {len(warning_items)} warning items.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to send email: {str(e)}')
            )
