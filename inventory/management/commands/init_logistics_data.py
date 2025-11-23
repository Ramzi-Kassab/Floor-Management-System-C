from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Initialize logistics master data (ConditionTypes, OwnershipTypes, UOMs, Categories)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing logistics master data...'))

        # Load fixtures in order
        fixtures = [
            ('initial_conditions.json', 'Condition Types'),
            ('initial_ownership.json', 'Ownership Types'),
            ('initial_uom.json', 'Units of Measure'),
            ('initial_categories.json', 'Item Categories'),
        ]

        for fixture_file, description in fixtures:
            try:
                self.stdout.write(f'Loading {description}...')
                call_command('loaddata', fixture_file, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f'✓ {description} loaded successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error loading {description}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\n=== Master Data Initialization Complete ==='))
        self.stdout.write('You can now create items, warehouses, and suppliers through the admin interface.')
