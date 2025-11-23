"""
Management command to create sample production data
Usage: python manage.py create_sample_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from production import models


class Command(BaseCommand):
    help = 'Create sample production data for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating sample production data...'))

        # Create Bit Designs
        designs = []
        
        # PDC Matrix Design
        design1, _ = models.BitDesign.objects.get_or_create(
            design_code='HD75WF',
            defaults={
                'bit_type': 'PDC',
                'body_material': 'MATRIX',
                'size_inch': 12.25,
                'blade_count': 7,
                'nozzle_count': 5,
                'description': 'Heavy duty PDC bit for hard formations',
                'active': True
            }
        )
        designs.append(design1)
        self.stdout.write(f'  ✓ Created design: {design1.design_code}')

        # PDC Steel Design
        design2, _ = models.BitDesign.objects.get_or_create(
            design_code='MS85ST',
            defaults={
                'bit_type': 'PDC',
                'body_material': 'STEEL',
                'size_inch': 8.5,
                'blade_count': 6,
                'nozzle_count': 4,
                'description': 'Medium soft formation steel body PDC',
                'active': True
            }
        )
        designs.append(design2)
        self.stdout.write(f'  ✓ Created design: {design2.design_code}')

        # Roller Cone Design
        design3, _ = models.BitDesign.objects.get_or_create(
            design_code='RC95TC',
            defaults={
                'bit_type': 'ROLLER_CONE',
                'size_inch': 9.5,
                'nozzle_count': 3,
                'description': 'Tri-cone bit for medium formations',
                'active': True
            }
        )
        designs.append(design3)
        self.stdout.write(f'  ✓ Created design: {design3.design_code}')

        # Create Design Revisions
        revisions = []
        for i, design in enumerate(designs, 1):
            revision, _ = models.BitDesignRevision.objects.get_or_create(
                mat_number=f'MAT-2025-{i:03d}-L4',
                defaults={
                    'design': design,
                    'level': 4,
                    'effective_from': timezone.now().date() - timedelta(days=30),
                    'active': True,
                    'remarks': f'Current production revision for {design.design_code}'
                }
            )
            revisions.append(revision)
            self.stdout.write(f'  ✓ Created revision: {revision.mat_number}')

        # Create Route Templates
        
        # Matrix PDC New Build Route
        route1, _ = models.RouteTemplate.objects.get_or_create(
            name='PDC Matrix New Build - Standard',
            defaults={
                'bit_type': 'PDC',
                'body_material': 'MATRIX',
                'for_order_type': 'NEW_BUILD',
                'department_focus': 'MATRIX_INFILTRATION',
                'active': True,
                'description': 'Standard matrix body PDC manufacturing process'
            }
        )
        
        if route1:
            steps_data = [
                (1, 'MOLD_PREP', 'Mold preparation and cleaning', 'MATRIX_INFILTRATION', 60),
                (2, 'POWDER_LOADING', 'Load powder and position inserts', 'MATRIX_INFILTRATION', 90),
                (3, 'INFILTRATION', 'Infiltration furnace cycle', 'MATRIX_INFILTRATION', 480),
                (4, 'COOLING', 'Controlled cooling and demolding', 'MATRIX_INFILTRATION', 240),
                (5, 'POST_MACHINING', 'Post-infiltration machining', 'FINISHING', 120),
                (6, 'WELD_UPPER', 'Weld upper API connector', 'FINISHING', 90),
                (7, 'BRAZING', 'Braze PDC cutters', 'FINISHING', 180),
                (8, 'FINAL_FINISH', 'Final finishing and cleaning', 'FINISHING', 60),
                (9, 'NDT_INSPECTION', 'Non-destructive testing', 'QC', 45),
                (10, 'THREAD_INSPECTION', 'API thread inspection', 'QC', 30),
                (11, 'FINAL_QC', 'Final quality control', 'QC', 30),
            ]
            
            for seq, code, desc, dept, duration in steps_data:
                models.RouteStepTemplate.objects.get_or_create(
                    route=route1,
                    sequence=seq,
                    defaults={
                        'process_code': code,
                        'description': desc,
                        'default_department': dept,
                        'estimated_duration_minutes': duration,
                        'is_mandatory': True
                    }
                )
        
        self.stdout.write(f'  ✓ Created route: {route1.name} with {route1.steps.count()} steps')

        # Steel PDC Route
        route2, _ = models.RouteTemplate.objects.get_or_create(
            name='PDC Steel New Build - Standard',
            defaults={
                'bit_type': 'PDC',
                'body_material': 'STEEL',
                'for_order_type': 'NEW_BUILD',
                'department_focus': 'FINISHING',
                'active': True,
                'description': 'Standard steel body PDC manufacturing process'
            }
        )
        
        if route2:
            steps_data = [
                (1, 'BODY_PREP', 'Steel body preparation', 'FINISHING', 60),
                (2, 'MACHINING', 'Precision machining', 'FINISHING', 120),
                (3, 'WELD_UPPER', 'Weld upper section', 'FINISHING', 90),
                (4, 'HARDFACING', 'Hardfacing application', 'FINISHING', 150),
                (5, 'BRAZING', 'Braze PDC cutters', 'FINISHING', 180),
                (6, 'FINAL_FINISH', 'Final finishing', 'FINISHING', 60),
                (7, 'NDT_INSPECTION', 'NDT inspection', 'QC', 45),
                (8, 'THREAD_INSPECTION', 'Thread inspection', 'QC', 30),
                (9, 'FINAL_QC', 'Final QC', 'QC', 30),
            ]
            
            for seq, code, desc, dept, duration in steps_data:
                models.RouteStepTemplate.objects.get_or_create(
                    route=route2,
                    sequence=seq,
                    defaults={
                        'process_code': code,
                        'description': desc,
                        'default_department': dept,
                        'estimated_duration_minutes': duration,
                        'is_mandatory': True
                    }
                )
        
        self.stdout.write(f'  ✓ Created route: {route2.name} with {route2.steps.count()} steps')

        # Create sample Work Orders
        customers = ['Schlumberger', 'Halliburton', 'Baker Hughes', 'NOV', 'Weatherford']
        
        for i in range(5):
            wo, created = models.WorkOrder.objects.get_or_create(
                wo_number=f'WO-2025-{i+1:04d}',
                defaults={
                    'order_type': 'NEW_BUILD' if i < 3 else 'REPAIR',
                    'design_revision': revisions[i % len(revisions)],
                    'customer_name': customers[i % len(customers)],
                    'rig': f'RIG-{i+1}',
                    'well': f'WELL-{i+1}',
                    'field': f'Field {chr(65+i)}',
                    'rent_or_sale_type': 'RENTAL' if i % 2 == 0 else 'SALE',
                    'priority': 'URGENT' if i == 0 else 'NORMAL',
                    'status': 'IN_PROGRESS' if i < 2 else 'OPEN',
                    'received_date': timezone.now().date() - timedelta(days=i*2),
                    'due_date': timezone.now().date() + timedelta(days=30-i*5),
                    'remarks': f'Sample work order {i+1}'
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created work order: {wo.wo_number}')

        # Create sample Job Cards
        work_orders = models.WorkOrder.objects.all()[:3]
        for i, wo in enumerate(work_orders):
            jc, created = models.JobCard.objects.get_or_create(
                jobcard_code=f'JC-2025-{i+1:04d}',
                defaults={
                    'work_order': wo,
                    'job_type': wo.order_type,
                    'is_repair': wo.order_type == 'REPAIR',
                    'department': 'MATRIX_INFILTRATION' if i == 0 else 'FINISHING',
                    'status': 'IN_PROGRESS' if i < 2 else 'RELEASED',
                    'planned_start': timezone.now() - timedelta(days=i),
                    'planned_end': timezone.now() + timedelta(days=7-i),
                    'notes': f'Sample job card {i+1}'
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created job card: {jc.jobcard_code}')
                
                # Create QR code for job card
                qr, _ = models.QRCode.objects.get_or_create(
                    job_card=jc,
                    defaults={'notes': f'Auto-generated for {jc.jobcard_code}'}
                )

        # Create Infiltration Batch
        batch, created = models.InfiltrationBatch.objects.get_or_create(
            batch_code='BATCH-2025-001',
            defaults={
                'furnace_id': 'FURNACE-1',
                'planned_start': timezone.now(),
                'planned_end': timezone.now() + timedelta(hours=12),
                'status': 'IN_FURNACE',
                'operator_name': 'John Smith',
                'temperature_profile': '{"stages": [{"temp": 1100, "duration": 180}, {"temp": 1150, "duration": 240}]}',
                'notes': 'Sample infiltration batch'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created infiltration batch: {batch.batch_code}')

        # Create Bit Instance
        instance, created = models.BitInstance.objects.get_or_create(
            serial_number='20250001',
            defaults={
                'design_revision': revisions[0],
                'body_material': 'MATRIX',
                'manufacturing_source': 'INTERNAL_MATRIX',
                'current_repair_index': 0,
                'status': 'IN_PRODUCTION',
                'notes': 'Sample bit instance'
            }
        )
        if created:
            self.stdout.write(f'  ✓ Created bit instance: {instance.serial_number}')

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.SUCCESS('\nSummary:'))
        self.stdout.write(f'  • Bit Designs: {models.BitDesign.objects.count()}')
        self.stdout.write(f'  • Design Revisions: {models.BitDesignRevision.objects.count()}')
        self.stdout.write(f'  • Route Templates: {models.RouteTemplate.objects.count()}')
        self.stdout.write(f'  • Route Steps: {models.RouteStepTemplate.objects.count()}')
        self.stdout.write(f'  • Work Orders: {models.WorkOrder.objects.count()}')
        self.stdout.write(f'  • Job Cards: {models.JobCard.objects.count()}')
        self.stdout.write(f'  • Bit Instances: {models.BitInstance.objects.count()}')
        self.stdout.write(f'  • Infiltration Batches: {models.InfiltrationBatch.objects.count()}')
        self.stdout.write(f'  • QR Codes: {models.QRCode.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nYou can now access the production dashboard at /production/'))
