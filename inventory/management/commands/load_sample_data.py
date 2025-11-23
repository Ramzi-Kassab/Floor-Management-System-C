"""
Management command to load comprehensive sample data for testing and demonstration.
Usage: python manage.py load_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from inventory.models import (
    Supplier, ItemCategory, UnitOfMeasure, Item,
    Warehouse, Location, ConditionType, OwnershipType,
    StockLevel, StockTransaction
)
from inventory.quality_control import (
    QualityInspection, ItemBatch, DefectiveItemDisposition,
    UsedItemTracking, ExpiredItemAction
)
from inventory.ksa_compliance import (
    CompanyProfile, ItemCertificate, CustomsDeclaration,
    CustomsDeclarationLine, Shipment
)
from purchasing.models import (
    PurchaseRequest, PurchaseRequestLine,
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine
)


class Command(BaseCommand):
    help = 'Load comprehensive sample data for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before loading',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Loading sample data...'))

        # Load data in dependency order
        self.load_users()
        self.load_ksa_company_profile()
        self.load_suppliers()
        self.load_categories_and_uoms()
        self.load_items()
        self.load_warehouses_and_locations()
        self.load_condition_and_ownership_types()
        self.load_stock_levels()
        self.load_stock_transactions()
        self.load_item_certificates()
        self.load_customs_declarations()
        self.load_shipments()
        self.load_quality_inspections()
        self.load_item_batches()
        self.load_used_items()
        self.load_purchase_requests()
        self.load_purchase_orders()
        self.load_goods_receipts()

        self.stdout.write(self.style.SUCCESS('✓ Sample data loaded successfully!'))
        self.print_summary()

    def clear_data(self):
        """Clear all existing data."""
        # Clear in reverse dependency order
        StockTransaction.objects.all().delete()
        StockLevel.objects.all().delete()
        GoodsReceiptLine.objects.all().delete()
        GoodsReceipt.objects.all().delete()
        PurchaseOrderLine.objects.all().delete()
        PurchaseOrder.objects.all().delete()
        PurchaseRequestLine.objects.all().delete()
        PurchaseRequest.objects.all().delete()
        UsedItemTracking.objects.all().delete()
        ExpiredItemAction.objects.all().delete()
        DefectiveItemDisposition.objects.all().delete()
        ItemBatch.objects.all().delete()
        QualityInspection.objects.all().delete()
        Shipment.objects.all().delete()
        CustomsDeclarationLine.objects.all().delete()
        CustomsDeclaration.objects.all().delete()
        ItemCertificate.objects.all().delete()
        Item.objects.all().delete()
        Location.objects.all().delete()
        Warehouse.objects.all().delete()
        ConditionType.objects.all().delete()
        OwnershipType.objects.all().delete()
        UnitOfMeasure.objects.all().delete()
        ItemCategory.objects.all().delete()
        Supplier.objects.all().delete()
        CompanyProfile.objects.all().delete()
        # Don't delete users to avoid removing superuser

    def load_users(self):
        """Create test users."""
        self.stdout.write('Creating users...')

        self.admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@drillingbits.sa',
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            self.admin_user.set_password('admin123')
            self.admin_user.save()

        self.operator_user, _ = User.objects.get_or_create(
            username='operator',
            defaults={
                'email': 'operator@drillingbits.sa',
                'first_name': 'Ahmed',
                'last_name': 'Al-Khalidi',
                'is_staff': True
            }
        )

        self.inspector_user, _ = User.objects.get_or_create(
            username='inspector',
            defaults={
                'email': 'inspector@drillingbits.sa',
                'first_name': 'Fatima',
                'last_name': 'Al-Otaibi',
                'is_staff': True
            }
        )

        self.supervisor_user, _ = User.objects.get_or_create(
            username='supervisor',
            defaults={
                'email': 'supervisor@drillingbits.sa',
                'first_name': 'Mohammed',
                'last_name': 'Al-Qahtani',
                'is_staff': True
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 4 users'))

    def load_ksa_company_profile(self):
        """Load company profile."""
        self.stdout.write('Creating company profile...')

        CompanyProfile.objects.get_or_create(
            id=1,
            defaults={
                'company_name_en': 'Advanced Drilling Bits Manufacturing Co.',
                'company_name_ar': 'شركة تصنيع البتات المتقدمة للحفر',
                'commercial_registration': '1010345678',
                'vat_registration_number': '300123456700003',
                'address_en': 'Industrial City, 2nd Industrial Area',
                'address_ar': 'المدينة الصناعية، المنطقة الصناعية الثانية',
                'city': 'Dammam',
                'postal_code': '34234',
                'country': 'SA',
                'phone': '0138901234',
                'email': 'info@drillingbits.sa',
                'industrial_license_number': 'IND-2020-5678',
                'zakat_certificate_number': 'ZAK-2024-1234',
                'einvoice_enabled': True
            }
        )

        self.stdout.write(self.style.SUCCESS('  ✓ Created company profile'))

    def load_suppliers(self):
        """Load suppliers."""
        self.stdout.write('Creating suppliers...')

        suppliers_data = [
            {'code': 'SUP-USA-001', 'name': 'Baker Hughes USA', 'country': 'US', 'city': 'Houston'},
            {'code': 'SUP-GER-001', 'name': 'Sandvik Coromant GmbH', 'country': 'DE', 'city': 'Düsseldorf'},
            {'code': 'SUP-CHN-001', 'name': 'Zhuzhou Cemented Carbide', 'country': 'CN', 'city': 'Zhuzhou'},
            {'code': 'SUP-KSA-001', 'name': 'Saudi Industrial Materials', 'country': 'SA', 'city': 'Riyadh'},
            {'code': 'SUP-ITA-001', 'name': 'Marchegiani SRL', 'country': 'IT', 'city': 'Milan'},
        ]

        for data in suppliers_data:
            Supplier.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'country': data['country'],
                    'city': data.get('city', ''),
                    'email': f"{data['code'].lower()}@supplier.com",
                    'active': True
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(suppliers_data)} suppliers'))

    def load_categories_and_uoms(self):
        """Load item categories and units of measure."""
        self.stdout.write('Creating categories and UOMs...')

        categories = [
            ('CUTTER', 'Cutters & Inserts'),
            ('MATRIX', 'Matrix Powders'),
            ('BINDER', 'Binder Materials'),
            ('STEEL', 'Steel Bodies'),
            ('COATING', 'Coating Materials'),
            ('CONSUMABLE', 'Consumables'),
        ]

        for code, name in categories:
            ItemCategory.objects.get_or_create(code=code, defaults={'name': name})

        uoms = [
            ('EA', 'Each', True),
            ('KG', 'Kilogram', False),
            ('TON', 'Metric Ton', False),
            ('LTR', 'Liter', False),
            ('M', 'Meter', False),
            ('BOX', 'Box', False),
        ]

        for code, name, is_base in uoms:
            UnitOfMeasure.objects.get_or_create(
                code=code,
                defaults={'name': name, 'is_base_unit': is_base}
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(categories)} categories, {len(uoms)} UOMs'))

    def load_items(self):
        """Load items."""
        self.stdout.write('Creating items...')

        category_cutter = ItemCategory.objects.get(code='CUTTER')
        category_matrix = ItemCategory.objects.get(code='MATRIX')
        category_binder = ItemCategory.objects.get(code='BINDER')

        uom_ea = UnitOfMeasure.objects.get(code='EA')
        uom_kg = UnitOfMeasure.objects.get(code='KG')

        items_data = [
            # Cutters
            {
                'item_code': 'CUT-PDC-001', 'name': 'PDC Cutter 13mm', 
                'category': category_cutter, 'uom': uom_ea,
                'item_type': 'CUTTER', 'reorder_level': 1000,
                'hs_code': '8207130000', 'country_of_origin': 'US',
                'vat_type': 'STANDARD', 'requires_saber_certificate': True
            },
            {
                'item_code': 'CUT-PDC-002', 'name': 'PDC Cutter 16mm',
                'category': category_cutter, 'uom': uom_ea,
                'item_type': 'CUTTER', 'reorder_level': 800,
                'hs_code': '8207130000', 'country_of_origin': 'US',
                'vat_type': 'STANDARD', 'requires_saber_certificate': True
            },
            {
                'item_code': 'CUT-TCI-001', 'name': 'Tungsten Carbide Insert',
                'category': category_cutter, 'uom': uom_ea,
                'item_type': 'CUTTER', 'reorder_level': 500,
                'hs_code': '8209001000', 'country_of_origin': 'DE',
                'vat_type': 'STANDARD', 'requires_saber_certificate': True
            },
            # Matrix powders
            {
                'item_code': 'MAT-WC-001', 'name': 'Tungsten Carbide Powder',
                'category': category_matrix, 'uom': uom_kg,
                'item_type': 'MATRIX_POWDER', 'reorder_level': 500,
                'hs_code': '2849901000', 'country_of_origin': 'CN',
                'vat_type': 'STANDARD', 'requires_saber_certificate': False
            },
            {
                'item_code': 'MAT-CO-001', 'name': 'Cobalt Powder',
                'category': category_matrix, 'uom': uom_kg,
                'item_type': 'MATRIX_POWDER', 'reorder_level': 300,
                'hs_code': '8105201000', 'country_of_origin': 'CN',
                'vat_type': 'STANDARD', 'requires_saber_certificate': False
            },
            # Binders
            {
                'item_code': 'BIN-EPX-001', 'name': 'Epoxy Resin',
                'category': category_binder, 'uom': uom_kg,
                'item_type': 'OTHER', 'reorder_level': 200,
                'hs_code': '3907300000', 'country_of_origin': 'IT',
                'vat_type': 'STANDARD', 'requires_saber_certificate': False
            },
        ]

        for data in items_data:
            Item.objects.get_or_create(item_code=data['item_code'], defaults=data)

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(items_data)} items'))

    def load_warehouses_and_locations(self):
        """Load warehouses and locations."""
        self.stdout.write('Creating warehouses and locations...')

        wh_main, _ = Warehouse.objects.get_or_create(
            code='WH-MAIN',
            defaults={'name': 'Main Warehouse - Dammam', 'active': True}
        )

        wh_qc, _ = Warehouse.objects.get_or_create(
            code='WH-QC',
            defaults={'name': 'Quality Control Area', 'active': True}
        )

        locations = [
            (wh_main, 'RACK-A1', 'Rack A - Level 1'),
            (wh_main, 'RACK-A2', 'Rack A - Level 2'),
            (wh_main, 'RACK-B1', 'Rack B - Level 1'),
            (wh_main, 'SILO-01', 'Powder Silo 1'),
            (wh_main, 'SILO-02', 'Powder Silo 2'),
            (wh_qc, 'QC-INSPECT', 'QC Inspection Area'),
            (wh_qc, 'QC-QUARANTINE', 'Quarantine Zone'),
        ]

        for warehouse, code, name in locations:
            Location.objects.get_or_create(
                warehouse=warehouse,
                code=code,
                defaults={'name': name, 'is_virtual': False}
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created 2 warehouses, {len(locations)} locations'))

    def load_condition_and_ownership_types(self):
        """Load condition and ownership types."""
        self.stdout.write('Creating condition and ownership types...')

        conditions = [
            ('NEW', 'New'),
            ('USED', 'Used'),
            ('REFURBISHED', 'Refurbished'),
            ('DAMAGED', 'Damaged'),
        ]

        ownerships = [
            ('OWN', 'Own Stock'),
            ('CONSIGNMENT', 'Consignment'),
            ('CUSTOMER', 'Customer Owned'),
        ]

        for code, name in conditions:
            ConditionType.objects.get_or_create(code=code, defaults={'name': name})

        for code, name in ownerships:
            OwnershipType.objects.get_or_create(code=code, defaults={'name': name})

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(conditions)} conditions, {len(ownerships)} ownerships'))

    def load_stock_levels(self):
        """Load stock levels."""
        self.stdout.write('Creating stock levels...')

        location_a1 = Location.objects.get(code='RACK-A1')
        location_silo1 = Location.objects.get(code='SILO-01')
        condition_new = ConditionType.objects.get(code='NEW')
        ownership_own = OwnershipType.objects.get(code='OWN')

        stock_data = [
            ('CUT-PDC-001', location_a1, 1250),
            ('CUT-PDC-002', location_a1, 950),
            ('CUT-TCI-001', location_a1, 675),
            ('MAT-WC-001', location_silo1, 750),
            ('MAT-CO-001', location_silo1, 420),
        ]

        for item_code, location, qty in stock_data:
            item = Item.objects.get(item_code=item_code)
            StockLevel.objects.get_or_create(
                item=item,
                location=location,
                condition_type=condition_new,
                ownership_type=ownership_own,
                defaults={'quantity': Decimal(str(qty))}
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(stock_data)} stock levels'))

    def load_stock_transactions(self):
        """Load stock transactions."""
        self.stdout.write('Creating stock transactions...')

        location_a1 = Location.objects.get(code='RACK-A1')
        condition_new = ConditionType.objects.get(code='NEW')
        ownership_own = OwnershipType.objects.get(code='OWN')
        item = Item.objects.get(item_code='CUT-PDC-001')

        transactions_data = [
            ('RECEIPT', 1000, 'GRN-2025-001', 5),
            ('RECEIPT', 500, 'GRN-2025-002', 3),
            ('ISSUE', -100, 'ISS-2025-001', 1),
            ('ADJUSTMENT', -150, 'ADJ-2025-001', 0),
        ]

        for trans_type, qty, ref, days_ago in transactions_data:
            StockTransaction.objects.get_or_create(
                reference=ref,
                defaults={
                    'item': item,
                    'to_location': location_a1 if qty > 0 else None,
                    'from_location': location_a1 if qty < 0 else None,
                    'condition_type': condition_new,
                    'ownership_type': ownership_own,
                    'transaction_type': trans_type,
                    'quantity': abs(Decimal(str(qty))),
                    'performed_by': self.operator_user,
                    'performed_at': timezone.now() - timedelta(days=days_ago)
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(transactions_data)} transactions'))

    def load_item_certificates(self):
        """Load item certificates."""
        self.stdout.write('Creating item certificates...')

        item = Item.objects.get(item_code='CUT-PDC-001')

        certs_data = [
            {
                'certificate_type': 'SABER',
                'certificate_number': 'SABER-2024-PDC-12345',
                'issue_date': date(2024, 1, 15),
                'expiry_date': date(2026, 1, 15),
                'status': 'VALID'
            },
            {
                'certificate_type': 'SASO',
                'certificate_number': 'SASO-2024-TCI-67890',
                'issue_date': date(2024, 3, 1),
                'expiry_date': date(2025, 3, 1),
                'status': 'VALID'
            },
        ]

        for cert_data in certs_data:
            ItemCertificate.objects.get_or_create(
                item=item,
                certificate_number=cert_data['certificate_number'],
                defaults=cert_data
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(certs_data)} certificates'))

    def load_customs_declarations(self):
        """Load customs declarations."""
        self.stdout.write('Creating customs declarations...')

        supplier = Supplier.objects.get(code='SUP-USA-001')
        item = Item.objects.get(item_code='CUT-PDC-001')

        declaration, created = CustomsDeclaration.objects.get_or_create(
            declaration_number='FASAH-2025-001234',
            defaults={
                'supplier': supplier,
                'bill_of_lading': 'BOL-USA-2025-001',
                'port_of_entry': 'Jeddah Islamic Port',
                'declaration_date': date.today() - timedelta(days=10),
                'clearance_status': 'CLEARED',
                'total_customs_duty': Decimal('2500.00'),
                'total_vat': Decimal('11250.00'),
                'other_fees': Decimal('250.00')
            }
        )

        if created:
            line = CustomsDeclarationLine.objects.create(
                customs_declaration=declaration,
                item=item,
                quantity=Decimal('1000'),
                unit_price=Decimal('50.00'),
                total_value=Decimal('50000.00'),
                hs_code='8207130000',
                customs_duty_rate=Decimal('5.00'),
                vat_rate=Decimal('15.00')
            )
            line.calculate_duties()
            line.save()

        self.stdout.write(self.style.SUCCESS('  ✓ Created 1 customs declaration'))

    def load_shipments(self):
        """Load shipments."""
        self.stdout.write('Creating shipments...')

        shipments_data = [
            {
                'shipment_number': 'SHIP-2025-001',
                'carrier': 'SMSA',
                'tracking_number': 'SMSA2025001234',
                'origin': 'Houston, TX',
                'destination': 'Dammam',
                'shipment_date': date.today() - timedelta(days=15),
                'status': 'DELIVERED',
                'estimated_delivery': date.today() - timedelta(days=3),
                'actual_delivery': date.today() - timedelta(days=2)
            },
            {
                'shipment_number': 'SHIP-2025-002',
                'carrier': 'ARAMEX',
                'tracking_number': 'ARAMEX9876543210',
                'origin': 'Riyadh',
                'destination': 'Dammam',
                'shipment_date': date.today() - timedelta(days=2),
                'status': 'IN_TRANSIT',
                'estimated_delivery': date.today() + timedelta(days=1)
            },
        ]

        for data in shipments_data:
            Shipment.objects.get_or_create(
                shipment_number=data['shipment_number'],
                defaults=data
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(shipments_data)} shipments'))

    def load_quality_inspections(self):
        """Load quality inspections."""
        self.stdout.write('Creating quality inspections...')

        item = Item.objects.get(item_code='CUT-PDC-001')
        location = Location.objects.get(code='QC-INSPECT')

        inspections_data = [
            {
                'inspection_number': 'QC-2025-001',
                'quantity_inspected': 100,
                'inspection_result': 'PASS',
                'passed_quantity': 98,
                'failed_quantity': 2,
                'days_ago': 5
            },
            {
                'inspection_number': 'QC-2025-002',
                'quantity_inspected': 50,
                'inspection_result': 'REJECT',
                'passed_quantity': 0,
                'failed_quantity': 50,
                'defect_category': 'DIMENSIONAL',
                'defect_severity': 'CRITICAL',
                'disposition': 'RETURN_TO_VENDOR',
                'days_ago': 2
            },
        ]

        for data in inspections_data:
            days_ago = data.pop('days_ago')
            QualityInspection.objects.get_or_create(
                inspection_number=data['inspection_number'],
                defaults={
                    **data,
                    'item': item,
                    'location': location,
                    'quantity_inspected': Decimal(str(data['quantity_inspected'])),
                    'passed_quantity': Decimal(str(data.get('passed_quantity', 0))),
                    'failed_quantity': Decimal(str(data.get('failed_quantity', 0))),
                    'inspection_date': date.today() - timedelta(days=days_ago),
                    'inspector': self.inspector_user
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(inspections_data)} inspections'))

    def load_item_batches(self):
        """Load item batches."""
        self.stdout.write('Creating item batches...')

        item = Item.objects.get(item_code='MAT-WC-001')
        location = Location.objects.get(code='SILO-01')

        batches_data = [
            {
                'batch_number': 'BATCH-2025-001',
                'quantity': 250,
                'manufacturing_date': date(2025, 1, 1),
                'expiry_date': date(2026, 1, 1),
                'is_quarantined': False
            },
            {
                'batch_number': 'BATCH-2025-002',
                'quantity': 500,
                'manufacturing_date': date(2025, 2, 1),
                'expiry_date': date(2026, 2, 1),
                'is_quarantined': False
            },
        ]

        for data in batches_data:
            ItemBatch.objects.get_or_create(
                batch_number=data['batch_number'],
                defaults={
                    **data,
                    'item': item,
                    'location': location,
                    'quantity': Decimal(str(data['quantity']))
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(batches_data)} batches'))

    def load_used_items(self):
        """Load used items tracking."""
        self.stdout.write('Creating used items...')

        category = ItemCategory.objects.get(code='CUTTER')
        uom = UnitOfMeasure.objects.get(code='EA')

        item, _ = Item.objects.get_or_create(
            item_code='USED-MOTOR-001',
            defaults={
                'name': 'Used Drill Motor PDM',
                'category': category,
                'unit_of_measure': uom,
                'item_type': 'OTHER',
                'reorder_level': 5
            }
        )

        location = Location.objects.get(code='RACK-B1')

        used_items_data = [
            {
                'tracking_number': 'USED-2025-001',
                'serial_number': 'PDM-12345',
                'condition_grade': 'B',
                'acquisition_source': 'CUSTOMER_RETURN',
                'hours_used': 150.5,
                'acquisition_days_ago': 30
            },
        ]

        for data in used_items_data:
            days_ago = data.pop('acquisition_days_ago')
            UsedItemTracking.objects.get_or_create(
                tracking_number=data['tracking_number'],
                defaults={
                    **data,
                    'item': item,
                    'location': location,
                    'hours_used': Decimal(str(data['hours_used'])),
                    'acquisition_date': date.today() - timedelta(days=days_ago),
                    'last_maintenance_date': date.today() - timedelta(days=10),
                    'next_maintenance_due': date.today() + timedelta(days=20)
                }
            )

        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(used_items_data)} used items'))

    def load_purchase_requests(self):
        """Load purchase requests."""
        self.stdout.write('Creating purchase requests...')

        item = Item.objects.get(item_code='CUT-PDC-001')

        pr, created = PurchaseRequest.objects.get_or_create(
            request_number='PR-2025-001',
            defaults={
                'requested_by': self.operator_user,
                'status': 'APPROVED',
                'notes': 'Reorder for main warehouse'
            }
        )

        if created:
            PurchaseRequestLine.objects.create(
                purchase_request=pr,
                item=item,
                quantity_requested=Decimal('500'),
                notes='Urgent - stock below reorder level'
            )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 1 purchase request'))

    def load_purchase_orders(self):
        """Load purchase orders."""
        self.stdout.write('Creating purchase orders...')

        supplier = Supplier.objects.get(code='SUP-USA-001')
        item = Item.objects.get(item_code='CUT-PDC-001')

        po, created = PurchaseOrder.objects.get_or_create(
            order_number='PO-2025-001',
            defaults={
                'supplier': supplier,
                'order_date': date.today() - timedelta(days=20),
                'status': 'RECEIVED',
                'total_amount': Decimal('25000.00')
            }
        )

        if created:
            PurchaseOrderLine.objects.create(
                purchase_order=po,
                item=item,
                quantity_ordered=Decimal('500'),
                unit_price=Decimal('50.00'),
                total_price=Decimal('25000.00')
            )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 1 purchase order'))

    def load_goods_receipts(self):
        """Load goods receipts."""
        self.stdout.write('Creating goods receipts...')

        po = PurchaseOrder.objects.get(order_number='PO-2025-001')
        item = Item.objects.get(item_code='CUT-PDC-001')
        location = Location.objects.get(code='RACK-A1')

        gr, created = GoodsReceipt.objects.get_or_create(
            grn_number='GRN-2025-001',
            defaults={
                'purchase_order': po,
                'receipt_date': date.today() - timedelta(days=15),
                'received_by': self.operator_user,
                'status': 'COMPLETED'
            }
        )

        if created:
            GoodsReceiptLine.objects.create(
                goods_receipt=gr,
                po_line=po.lines.first(),
                item=item,
                location=location,
                quantity_received=Decimal('500'),
                quantity_accepted=Decimal('498'),
                quantity_rejected=Decimal('2')
            )

        self.stdout.write(self.style.SUCCESS('  ✓ Created 1 goods receipt'))

    def print_summary(self):
        """Print summary of loaded data."""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('DATA LOADING SUMMARY'))
        self.stdout.write('='*60)
        
        summary = [
            ('Users', User.objects.count()),
            ('Company Profiles', CompanyProfile.objects.count()),
            ('Suppliers', Supplier.objects.count()),
            ('Item Categories', ItemCategory.objects.count()),
            ('Units of Measure', UnitOfMeasure.objects.count()),
            ('Items', Item.objects.count()),
            ('Warehouses', Warehouse.objects.count()),
            ('Locations', Location.objects.count()),
            ('Stock Levels', StockLevel.objects.count()),
            ('Stock Transactions', StockTransaction.objects.count()),
            ('Item Certificates', ItemCertificate.objects.count()),
            ('Customs Declarations', CustomsDeclaration.objects.count()),
            ('Shipments', Shipment.objects.count()),
            ('Quality Inspections', QualityInspection.objects.count()),
            ('Item Batches', ItemBatch.objects.count()),
            ('Used Items', UsedItemTracking.objects.count()),
            ('Purchase Requests', PurchaseRequest.objects.count()),
            ('Purchase Orders', PurchaseOrder.objects.count()),
            ('Goods Receipts', GoodsReceipt.objects.count()),
        ]
        
        for label, count in summary:
            self.stdout.write(f'{label:.<40} {count:>5}')
        
        self.stdout.write('='*60 + '\n')
        
        # Test credentials
        self.stdout.write(self.style.SUCCESS('TEST LOGIN CREDENTIALS:'))
        self.stdout.write('  Admin:      username=admin      password=admin123')
        self.stdout.write('  Operator:   username=operator   password=password123')
        self.stdout.write('  Inspector:  username=inspector  password=password123')
        self.stdout.write('  Supervisor: username=supervisor password=password123')
        self.stdout.write('')
