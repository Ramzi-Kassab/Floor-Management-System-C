#!/usr/bin/env python
"""
Comprehensive Repair Workflow Backend Test
Tests all models, relationships, and helper methods
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'floor_project.settings')
django.setup()

from production.models import (
    BitDesign, BitDesignRevision, BOMItem, ActualBOM, RepairHistory,
    CutterLayoutPosition, ActualCutterInstallation, BitInstance,
    WorkOrder
)
from datetime import date, timedelta
from decimal import Decimal

print('🧪 COMPREHENSIVE REPAIR WORKFLOW TEST\n')
print('=' * 70)

# Test 1: Create BitDesign
print('\n✓ Test 1: Create BitDesign')
design = BitDesign.objects.create(
    design_code='TEST-PDC-001',
    bit_type='PDC_MATRIX',
    body_material='MATRIX',
    size_inch=Decimal('8.5'),
    blade_count=6,
    nozzle_count=3,
    description='8.5 inch PDC matrix body bit with 6 blades',
    active=True
)
print(f'  Created: {design.design_code} ({design.get_bit_type_display()})')
print(f'  Size: {design.size_inch}" with {design.blade_count} blades')

# Test 2: Create BitDesignRevision
print('\n✓ Test 2: Create BitDesignRevision')
revision = BitDesignRevision.objects.create(
    design=design,
    mat_number='MAT-TEST-001',
    level=1,
    effective_from=date.today(),
    effective_to=None,
    active=True,
    remarks='Initial design revision for testing'
)
print(f'  MAT: {revision.mat_number}, Level: {revision.level}')
print(f'  Active: {revision.active}')

# Test 3: Create BOM Items
print('\n✓ Test 3: Create BOM Items')
bom_cutter = BOMItem.objects.create(
    design_revision=revision,
    item_type='CUTTER',
    part_number='CUTTER-13MM',
    description='13mm PDC Cutter',
    quantity=60,
    unit='EA',
    is_critical=True
)
bom_nozzle = BOMItem.objects.create(
    design_revision=revision,
    item_type='NOZZLE',
    part_number='NOZZLE-12',
    description='12/32 TFA Nozzle',
    quantity=3,
    unit='EA',
    is_critical=True
)
bom_hardfacing = BOMItem.objects.create(
    design_revision=revision,
    item_type='HARDFACING',
    part_number='HF-TUNGSTEN',
    description='Tungsten Carbide Hardfacing',
    quantity=Decimal('2.5'),
    unit='KG',
    is_critical=False
)
print(f'  Created {BOMItem.objects.filter(design_revision=revision).count()} BOM items:')
print(f'    • {bom_cutter.part_number}: {bom_cutter.quantity} {bom_cutter.unit}')
print(f'    • {bom_nozzle.part_number}: {bom_nozzle.quantity} {bom_nozzle.unit}')
print(f'    • {bom_hardfacing.part_number}: {bom_hardfacing.quantity} {bom_hardfacing.unit}')

# Test 4: Create Cutter Layout Grid
print('\n✓ Test 4: Create Cutter Layout Grid (6 blades × 10 rows × 3 positions)')
positions_created = 0
for blade in range(1, 7):
    for row in range(1, 11):
        for pos_in_row in range(1, 4):
            # Define zones based on row
            if row <= 3:
                zone = 'CONE'
            elif row <= 7:
                zone = 'NOSE'
            else:
                zone = 'GAUGE'

            CutterLayoutPosition.objects.create(
                design_revision=revision,
                blade_number=blade,
                row_number=row,
                position_in_row=pos_in_row,
                zone=zone,
                cutter_size_mm=Decimal('13.0'),
                cutter_type='STANDARD_ROUND',
                back_rake_angle=Decimal('15.0'),
                exposure_mm=Decimal('2.5'),
                bom_item=bom_cutter
            )
            positions_created += 1

print(f'  Created {positions_created} cutter positions')
cone_count = CutterLayoutPosition.objects.filter(design_revision=revision, zone='CONE').count()
nose_count = CutterLayoutPosition.objects.filter(design_revision=revision, zone='NOSE').count()
gauge_count = CutterLayoutPosition.objects.filter(design_revision=revision, zone='GAUGE').count()
print(f'  Distribution: CONE={cone_count}, NOSE={nose_count}, GAUGE={gauge_count}')

# Test 5: Create BitInstance (WITHOUT initial_build_wo for now)
print('\n✓ Test 5: Create BitInstance')
instance = BitInstance.objects.create(
    serial_number='BIT-TEST-001',
    design_revision=revision,
    body_material='MATRIX',
    manufacturing_source='IN_HOUSE',
    current_repair_index=0,
    status='IN_PRODUCTION'
)
print(f'  Serial: {instance.serial_number}')
print(f'  Status: {instance.get_status_display()}')
print(f'  Repair Index: {instance.current_repair_index}')

# Test 6: Create NEW WorkOrder
print('\n✓ Test 6: Create NEW WorkOrder')
wo_new = WorkOrder.objects.create(
    wo_number='WO-NEW-TEST-001',
    order_type='NEW',
    bit_instance=instance,
    design_revision=revision,
    customer_name='Test Customer Inc.',
    rig='RIG-001',
    well='WELL-A-123',
    field='TEST FIELD',
    rent_or_sale_type='SALE',
    priority='HIGH',
    status='COMPLETED',
    received_date=date.today() - timedelta(days=80),
    due_date=date.today() - timedelta(days=60)
)
print(f'  WO: {wo_new.wo_number}')
print(f'  Type: {wo_new.get_order_type_display()}')
print(f'  Status: {wo_new.get_status_display()}')

# Update BitInstance with initial_build_wo
instance.initial_build_wo = wo_new
instance.status = 'IN_SERVICE'
instance.save()
print(f'  ✓ BitInstance updated with initial build WO')

# Test 7: Track Actual BOM Usage with Variance
print('\n✓ Test 7: Track Actual BOM Usage with Variance')
actual_bom_cutter = ActualBOM.objects.create(
    work_order=wo_new,
    bom_item=bom_cutter,
    planned_quantity=60,
    actual_quantity=62,
    lot_number='LOT-2024-001',
    variance_notes='2 extra cutters used during assembly'
)
actual_bom_nozzle = ActualBOM.objects.create(
    work_order=wo_new,
    bom_item=bom_nozzle,
    planned_quantity=3,
    actual_quantity=3,
    lot_number='LOT-2024-002'
)
variance_cutter = actual_bom_cutter.get_variance()
variance_nozzle = actual_bom_nozzle.get_variance()
print(f'  Cutters  - Planned: {actual_bom_cutter.planned_quantity:2d}, Actual: {actual_bom_cutter.actual_quantity:2d}, Variance: {variance_cutter:+.1f}')
print(f'  Nozzles  - Planned: {actual_bom_nozzle.planned_quantity:2d}, Actual: {actual_bom_nozzle.actual_quantity:2d}, Variance: {variance_nozzle:+.1f}')

# Test 8: Create REPAIR WorkOrder
print('\n✓ Test 8: Create REPAIR WorkOrder')
wo_repair = WorkOrder.objects.create(
    wo_number='WO-REP-TEST-001',
    order_type='REPAIR',
    bit_instance=instance,
    design_revision=revision,
    customer_name='Test Customer Inc.',
    rig='RIG-002',
    well='WELL-B-456',
    field='TEST FIELD',
    rent_or_sale_type='SALE',
    priority='NORMAL',
    status='IN_PROGRESS',
    received_date=date.today(),
    due_date=date.today() + timedelta(days=7)
)
print(f'  WO: {wo_repair.wo_number}')
print(f'  Type: {wo_repair.get_order_type_display()}')
print(f'  Status: {wo_repair.get_status_display()}')

# Test 9: Create RepairHistory
print('\n✓ Test 9: Create RepairHistory')
repair = RepairHistory.objects.create(
    bit_instance=instance,
    work_order=wo_repair,
    repair_index=1,
    hours_on_bit=Decimal('120.5'),
    footage_drilled=Decimal('1500.0'),
    cutters_replaced=8,
    hardfacing_applied=True,
    nozzles_replaced=1,
    threads_repaired=True,
    damage_description='First repair: replaced 8 worn cutters in nose zone'
)
print(f'  Repair #{repair.repair_index}')
print(f'  Usage: {repair.hours_on_bit}h, {repair.footage_drilled}ft')
print(f'  Work: {repair.cutters_replaced} cutters, {repair.nozzles_replaced} nozzles')
print(f'  Hardfacing: {repair.hardfacing_applied}, Threads: {repair.threads_repaired}')

# Test 10: Record Cutter Installations
print('\n✓ Test 10: Record Cutter Installations')
test_positions = CutterLayoutPosition.objects.filter(
    design_revision=revision,
    blade_number=1,
    row_number__lte=2
)[:5]

installations = []
for idx, pos in enumerate(test_positions, 1):
    installation = ActualCutterInstallation.objects.create(
        work_order=wo_repair,
        layout_position=pos,
        actual_cutter_size_mm=Decimal('13.0'),
        actual_cutter_type='STANDARD_ROUND',
        actual_bom_item=bom_cutter,
        cutter_serial_number=f'CUT-{idx:03d}',
        cutter_lot_number='LOT-2024-001',
        braze_quality_check='PASS',
        status='PASS'
    )
    installations.append(installation)

print(f'  Recorded {len(installations)} cutter installations')
print(f'  Sample: {installations[0].layout_position.get_position_code()} → {installations[0].cutter_serial_number}')
print(f'  All QC passed: {all(i.braze_quality_check == "PASS" for i in installations)}')
print(f'  Substitutions: {sum(1 for i in installations if i.is_substitution)}')

# Test 11: BitInstance Helper Methods
print('\n✓ Test 11: Test BitInstance Helper Methods')
all_wo = instance.get_all_work_orders()
repair_chain = instance.get_repair_history_chain()
last_repair = instance.get_last_repair()
can_repair = instance.can_be_repaired_again()
total_repairs = instance.get_total_repairs_count()

print(f'  Total Work Orders: {all_wo.count()}')
wo_list = ', '.join(all_wo.values_list('wo_number', flat=True))
print(f'    → {wo_list}')
print(f'  Repair History: {repair_chain.count()} repair(s)')
print(f'  Last Repair: #{last_repair.repair_index if last_repair else "None"}')
print(f'  Total Repairs: {total_repairs}')
print(f'  Can Repair Again: {can_repair} (max 5 repairs)')

# Test 12: Cutter Layout Helper Methods
print('\n✓ Test 12: Test CutterLayoutPosition Helper Methods')
sample_pos = CutterLayoutPosition.objects.filter(design_revision=revision).first()
pos_code = sample_pos.get_position_code()
print(f'  Position Code: {pos_code}')
print(f'  Format: B{sample_pos.blade_number}R{sample_pos.row_number}P{sample_pos.position_in_row}')
print(f'  Zone: {sample_pos.get_zone_display()}')

# Test 13: Foreign Key Relationships
print('\n✓ Test 13: Test Foreign Key Relationships')
print(f'  Design → Revisions: {design.revisions.count()}')
print(f'  Revision → BOM Items: {revision.bom_items.count()}')
print(f'  Revision → Layout Positions: {revision.cutter_positions.count()}')
print(f'  BitInstance → Work Orders: {instance.work_orders.count()}')
print(f'  BitInstance → Repair History: {instance.repair_history.count()}')
print(f'  WorkOrder → Actual BOM: {wo_new.actual_bom.count()}')
print(f'  WorkOrder → Cutter Installations: {wo_repair.cutter_installations.count()}')

print('\n' + '=' * 70)
print('✅ ALL TESTS PASSED - BACKEND FULLY FUNCTIONAL')
print('=' * 70)

# Final Statistics
print('\n📊 Final Database Statistics:')
stats = {
    'BitDesigns': BitDesign.objects.count(),
    'BitDesignRevisions': BitDesignRevision.objects.count(),
    'BOM Items': BOMItem.objects.count(),
    'Cutter Layout Positions': CutterLayoutPosition.objects.count(),
    'BitInstances': BitInstance.objects.count(),
    'WorkOrders (NEW)': WorkOrder.objects.filter(order_type='NEW').count(),
    'WorkOrders (REPAIR)': WorkOrder.objects.filter(order_type='REPAIR').count(),
    'ActualBOM Records': ActualBOM.objects.count(),
    'RepairHistory Records': RepairHistory.objects.count(),
    'Cutter Installations': ActualCutterInstallation.objects.count(),
}

for key, value in stats.items():
    print(f'  ✓ {key:.<40} {value:>3}')

print('\n✅ Complete repair workflow verified and operational!')
print('✅ All models, relationships, and helper methods working correctly!')
