from django.core.management.base import BaseCommand
from inventory.models import Warehouse, Location


class Command(BaseCommand):
    help = 'Create sample warehouse with locations for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample warehouse and locations...'))

        # Create main warehouse
        warehouse, created = Warehouse.objects.get_or_create(
            code='WH-MAIN',
            defaults={
                'name': 'Main Warehouse',
                'address': 'Factory Floor, Building A',
                'description': 'Primary warehouse for drilling bit components',
                'active': True
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created warehouse: {warehouse.code}'))
        else:
            self.stdout.write(f'  Warehouse {warehouse.code} already exists')

        # Create sample locations
        locations_data = [
            ('CUTTER-RACK-01', 'Cutter Storage Rack 01', 'Storage rack for PDC cutters', False),
            ('CUTTER-RACK-02', 'Cutter Storage Rack 02', 'Storage rack for PDC cutters', False),
            ('POWDER-SILO-1', 'Matrix Powder Silo 1', 'Bulk storage for matrix powder', False),
            ('POWDER-SILO-2', 'Matrix Powder Silo 2', 'Bulk storage for matrix powder', False),
            ('STEEL-AREA-A', 'Steel Storage Area A', 'Steel bodies and forgings area', False),
            ('JV-BODY-AREA', 'JV Body Storage', 'Storage for semi-finished JV bodies', False),
            ('UPPER-RACK', 'Upper Section Rack', 'API connection upper sections', False),
            ('CONSUMABLE-01', 'Consumables Area 01', 'General consumables storage', False),
            ('TOOL-ROOM', 'Tool Room', 'Manufacturing tools storage', False),
            ('ADJUSTMENT', 'Adjustment Location', 'Virtual location for stock adjustments', True),
            ('SCRAP', 'Scrap Area', 'Virtual location for scrapped items', True),
        ]

        created_count = 0
        for code, name, desc, is_virtual in locations_data:
            location, created = Location.objects.get_or_create(
                warehouse=warehouse,
                code=code,
                defaults={
                    'name': name,
                    'description': desc,
                    'is_virtual': is_virtual
                }
            )
            if created:
                created_count += 1
                status = '(Virtual)' if is_virtual else ''
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created location: {code} {status}'))

        self.stdout.write(self.style.SUCCESS(f'\n=== Created {created_count} new locations ==='))
        self.stdout.write(f'Total locations in {warehouse.code}: {warehouse.locations.count()}')
