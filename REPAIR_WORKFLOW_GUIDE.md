# Repair Workflow Guide
## Complete Repair Management System for Drilling Bits

*Version 1.0 - Last Updated: 2025-11-23*

---

## Overview

The Production Department system now includes comprehensive repair workflow management that tracks:
- Bill of Materials (BOM) for each bit design
- Complete repair history for every bit instance
- Evaluation-based repair routing intelligence
- Material usage tracking (planned vs. actual)
- Repair cost estimation and resource planning

---

## Table of Contents

1. [Repair Workflow Overview](#repair-workflow-overview)
2. [Bill of Materials (BOM) Management](#bill-of-materials-bom-management)
3. [Receiving a Bit for Repair](#receiving-a-bit-for-repair)
4. [Evaluation and Repair Decision](#evaluation-and-repair-decision)
5. [Creating a Repair Work Order](#creating-a-repair-work-order)
6. [Executing the Repair](#executing-the-repair)
7. [Tracking Repair History](#tracking-repair-history)
8. [Viewing Complete Bit History](#viewing-complete-bit-history)
9. [Material Usage Tracking](#material-usage-tracking)
10. [Repair Analytics](#repair-analytics)

---

## Repair Workflow Overview

### Complete Repair Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                   REPAIR WORKFLOW LIFECYCLE                      │
└─────────────────────────────────────────────────────────────────┘

1. BIT RECEIVED
   ↓
   → BitReceive record created
   → Bit status: IN_REPAIR
   → Photos and documentation attached

2. INITIAL EVALUATION
   ↓
   → EvaluationSummary created
   → Overall condition assessed
   → Recommended action determined

3. REPAIR DECISION (NEW!)
   ↓
   → RepairDecision auto-generated
   → Required processes identified:
     • Cutter replacement?
     • Nozzle replacement?
     • Hardfacing needed?
     • Thread repair?
     • Gauge repair?
     • NDT testing?
   → Route template recommended
   → Resource estimates calculated

4. WORK ORDER CREATION
   ↓
   → Work Order (type=REPAIR)
   → Links to bit_instance
   → References evaluation
   → BOM copied from design

5. REVIEW PREVIOUS REPAIRS (NEW!)
   ↓
   → Check repair_history
   → Review previous_repair record
   → Check BOM from last repair
   → Review remarks from previous WOs

6. JOB CARD & ROUTING
   ↓
   → Job Card created
   → Route steps generated (based on RepairDecision)
   → QR codes generated for each step

7. REPAIR EXECUTION
   ↓
   → Operators scan QR codes
   → Time tracking automatic
   → Materials consumed recorded in ActualBOM

8. REPAIR COMPLETION
   ↓
   → RepairHistory record created/updated
   → Cutters replaced count
   → Nozzles replaced count
   → Work performed documented
   → Repair notes captured

9. BIT RELEASED
   ↓
   → current_repair_index incremented (e.g., R1 → R2)
   → BitRelease record
   → Certificates generated
```

---

## Bill of Materials (BOM) Management

### What is a BOM?

A Bill of Materials (BOM) is the complete list of materials, components, and parts needed to manufacture or repair a bit design.

### Creating a BOM for a Design

**Location:** Django Admin → BOM Items → Add BOM Item

**Or:** Django Admin → Bit Design Revisions → (Select design) → BOM Items (inline)

**Fields:**
```
Design Revision:     MAT-001 (select the design this BOM applies to)
Item Type:           [Choose from dropdown]
                     • CUTTER - PDC Cutter
                     • NOZZLE - Nozzle
                     • BEARING - Bearing
                     • SEAL - Seal
                     • HARDFACING - Hardfacing Material
                     • POWDER - Matrix Powder
                     • BINDER - Binder/Infiltrant
                     • THREAD_COMPOUND - Thread Compound
                     • OTHER - Other Component

Part Number:         e.g., "PDC-1308-01"
Description:         "13mm PDC Cutter, Premium Grade"
Quantity:            24 (number needed per bit)
Unit:                EA (each), LB (pounds), KG (kilograms), etc.
Manufacturer:        "Smith International"
Grade:               "Premium, API Grade 5"
Is Critical:         ☑ (check if this component is critical and requires tracking)
Notes:               Any special notes about this component
```

### Example BOM for 12.25" PDC Bit

| Part Number | Description | Qty | Unit | Type | Critical |
|------------|-------------|-----|------|------|----------|
| PDC-1308-01 | 13mm PDC Cutter Premium | 24 | EA | CUTTER | ☑ |
| PDC-1613-01 | 16mm PDC Cutter Premium | 12 | EA | CUTTER | ☑ |
| NOZ-14-TFA | 14/32" Nozzle | 6 | EA | NOZZLE | ☐ |
| HF-TUNGSTEN | Tungsten Carbide Hardfacing | 5 | LB | HARDFACING | ☐ |
| SEAL-API-4.5 | API 4.5" Pin Seal | 1 | EA | SEAL | ☑ |

---

## Receiving a Bit for Repair

### Step 1: Create Bit Receive Record

**Location:** Production → Bit Receiving (or Django Admin)

**Information to Capture:**
```
Receive Number:      AUTO-GENERATED (e.g., RCV-2025-0001)
Bit Instance:        Select from dropdown (existing bits only)
Customer Name:       "Aramco Well Services"
Received Date:       2025-11-23
Received By:         [Your name / auto from login]
Transport Company:   "DHL Express"
Tracking Number:     "123456789"

Package Condition:   [Select]
                     • GOOD - Package intact
                     • DAMAGED - Package damaged
                     • PARTIAL - Partial shipment

Inspection Status:   PENDING (will update after inspection)

Documentation:
Customer PO:         ☑ (check if PO is included)
Packing Slip:        ☑
Bit Record:          ☑ (check if bit record/history is included)
Photos:              Upload photos of received bit

Remarks:             "Bit shows significant wear on gauge pads.
                      Customer reports 450 hours, 2,800 ft drilled"
```

### Step 2: Initial Inspection

After receiving, the QC team inspects the bit:
- Visual inspection
- Measurements (gauge, cutters, threads)
- Photos of damage
- Update **Inspection Status** to "INSPECTED"

---

## Evaluation and Repair Decision

### Step 3: Create Evaluation Summary

**Location:** Production → Evaluations → New Evaluation

**Evaluation Form:**
```
Job Card:            (Create a preliminary job card or select existing)
Evaluation Date:     2025-11-23
Evaluator Name:      "Ahmed Al-Saudi" (QC Inspector)

Overall Condition:   [Select]
                     • OK - Bit in good condition
                     • MINOR_DAMAGE - Minor damage, repairable
                     • MAJOR_DAMAGE - Major damage, extensive repair
                     • SCRAP - Beyond economical repair

Recommended Action:  [Select]
                     • RETURN_AS_IS - Return to customer as-is
                     • REPAIR - Proceed with repair
                     • SCRAP - Scrap the bit

Remarks:             "Bit HD75WF S/N 12345-R1 returned from Rig #7.

                      OBSERVED DAMAGE:
                      - 8 cutters broken/missing (gauge row)
                      - 3 cutters chipped (inner rows)
                      - Hardfacing worn 60% on gauge pads
                      - Pin threads: minor scoring
                      - Box threads: acceptable
                      - Gauge: 0.020" under nominal

                      RECOMMENDATION:
                      - Replace 8 gauge cutters
                      - Replace 3 inner cutters (total 11)
                      - Re-hardfacing on gauge pads
                      - Light thread dressing on pin
                      - Check balance after assembly

                      Estimated repair time: 16 hours
                      Recommended route: REPAIR-HEAVY"
```

### Step 4: Create Repair Decision (AUTO or MANUAL)

**Option A: Automatic (Recommended)**

The system can automatically create a RepairDecision based on evaluation remarks. Engineering or supervisor reviews and adjusts.

**Option B: Manual**

**Location:** Django Admin → Repair Decisions → Add Repair Decision

**Repair Decision Form:**
```
Evaluation Summary:  [Select the evaluation created above]

REQUIRED PROCESSES:
☑ Needs Cutter Replacement
☑ Needs Nozzle Replacement (if damaged)
☑ Needs Hardfacing
☑ Needs Thread Repair
☐ Needs Gauge Repair (not needed in this case)
☑ Needs Balance Check
☑ Needs NDT (recommended)

RESOURCE ESTIMATES:
Estimated Hours:           16
Estimated Cutter Count:    11

Recommended Route:         REPAIR-HEAVY (select from route templates)

Decision Notes:            "Heavy repair required due to extensive cutter damage.
                            Will use REPAIR-HEAVY route template which includes:
                            1. Disassembly
                            2. Cleaning & inspection
                            3. Cutter removal (damaged)
                            4. Cutter installation (11 new)
                            5. Hardfacing application
                            6. Thread dressing
                            7. Assembly
                            8. Balance check
                            9. NDT (MPI on cutters)
                            10. Final QC"
```

---

## Creating a Repair Work Order

### Step 5: Reference Previous Repairs & BOM

**BEFORE creating a new repair work order, ALWAYS review:**

#### A. Check Previous Repairs

**Method 1: Via Bit Instance Detail Page**
```python
# In Django shell or via custom view
bit = BitInstance.objects.get(serial_number="12345")

# Get all previous repairs
previous_repairs = bit.get_repair_history_chain()

for repair in previous_repairs:
    print(f"Repair R{repair.repair_index}")
    print(f"  Work Order: {repair.work_order.wo_number}")
    print(f"  Date: {repair.repair_completed_date}")
    print(f"  Cutters Replaced: {repair.cutters_replaced}")
    print(f"  Nozzles Replaced: {repair.nozzles_replaced}")
    print(f"  Damage: {repair.damage_description}")
    print(f"  Notes: {repair.repair_notes}")
    print("---")
```

**Method 2: Via Django Admin**

Django Admin → Repair Histories → Filter by bit_instance → Review all R1, R2, R3 records

**What to Look For:**
- Common failure modes (same cutters failing?)
- Previous materials used
- Previous repair notes
- Root cause of damage

#### B. Check Previous Work Order Remarks

```python
# Get all work orders for this bit
work_orders = bit.get_all_work_orders()

for wo in work_orders:
    print(f"WO: {wo.wo_number} ({wo.order_type})")
    print(f"  Remarks: {wo.remarks}")
```

**Look for:**
- Customer feedback
- Field performance notes
- Special instructions
- Known issues

#### C. Review BOM from Design

**Location:** Django Admin → Bit Design Revisions → (Select design) → BOM Items

**Check:**
- Standard components for this design
- Cutter specifications (size, grade, manufacturer)
- Material specifications
- Any recent BOM changes

### Step 6: Create Repair Work Order

**Location:** Production → Work Orders → Create New

**Work Order Form:**
```
WO Number:           WO-2025-R-0042 (auto-generated)
Order Type:          REPAIR (CRITICAL!)
Bit Instance:        Select: 12345 (existing bit)
Design Revision:     MAT-001 (should match bit's design)

Customer Information:
Customer Name:       "Aramco Well Services"
Rig:                 "Rig #7"
Well:                "Well A-123"
Field:               "Ghawar Field"

Commercial:
Rent or Sale Type:   RENTAL (or WARRANTY if under warranty)
Priority:            HIGH (based on customer urgency)
Status:              DRAFT (will change to OPEN when ready)

Scheduling:
Received Date:       2025-11-23 (date bit was received)
Due Date:            2025-11-30 (customer deadline)

Remarks:             "REPAIR WORK ORDER - R2 (Second Repair)

                      REFERENCE TO PREVIOUS REPAIRS:
                      - R1 (WO-2024-R-0123, completed 2024-08-15)
                        → 6 cutters replaced
                        → Hardfacing applied
                        → Returned to service
                        → Lasted 450 hours before this return

                      CURRENT REPAIR REQUIREMENTS:
                      Based on Evaluation EVAL-2025-0012:
                      - Replace 11 cutters (8 gauge + 3 inner)
                      - Re-hardfacing on gauge pads
                      - Thread dressing on pin
                      - Balance check mandatory
                      - NDT required (MPI)

                      BOM NOTES:
                      - Use premium grade cutters (PDC-1308-01)
                      - Customer prefers Smith Int'l cutters
                      - Tungsten carbide hardfacing only

                      CUSTOMER NOTES:
                      - Bit was drilling hard limestone
                      - Customer reports no abnormal vibration
                      - Customer satisfied with R1 performance
                      - Rush job - need by 2025-11-30"
```

### Step 7: Copy Planned BOM to Actual BOM

When the work order is created, the system can automatically copy BOM items from the design to ActualBOM records for this work order:

```python
# This happens automatically when WO is created (can be done via signal)
wo = WorkOrder.objects.get(wo_number="WO-2025-R-0042")
design_revision = wo.design_revision

# Copy each BOM item to ActualBOM
for bom_item in design_revision.bom_items.all():
    ActualBOM.objects.create(
        work_order=wo,
        bom_item=bom_item,
        planned_quantity=bom_item.quantity,
        # actual_quantity will be filled during repair
    )
```

**Manual Alternative:**

Django Admin → Actual BOMs → Add ActualBOM (for each component)

---

## Executing the Repair

### Step 8: Create Job Card

**Location:** Production → Job Cards → Create New

```
Job Card Code:       JC-2025-0089 (auto-generated)
Work Order:          WO-2025-R-0042
Job Type:            REPAIR
Is Repair:           ☑ (checked)
Department:          REPAIR (Repair Department)
Status:              RELEASED (ready for production)
```

### Step 9: Route Generation

**Option A: Auto-generate from RepairDecision**

The system can automatically generate route steps based on the RepairDecision:

```python
job_card = JobCard.objects.get(jobcard_code="JC-2025-0089")
repair_decision = RepairDecision.objects.get(
    evaluation_summary__job_card=job_card
)

# Generate steps based on required processes
if repair_decision.needs_cutter_replacement:
    # Add cutter removal steps
    # Add cutter installation steps

if repair_decision.needs_hardfacing:
    # Add hardfacing steps

# etc.
```

**Option B: Use Route Template**

Select the recommended route template (e.g., "REPAIR-HEAVY") and generate steps from it.

### Step 10: Print Route Sheet with QR Codes

**Location:** Production → Job Cards → (Select job card) → Print Route Sheet

This generates a printable route sheet with:
- All process steps
- QR code for each step
- Status tracking
- Operator signature fields

### Step 11: Shop Floor Execution

Operators scan QR codes to start/complete each process:

1. **Scan 1 (Start):** Operator scans QR code → Process status: IN_PROGRESS
2. **Perform Work:** Operator completes the process
3. **Scan 2 (Complete):** Operator scans same QR code → Process status: DONE
4. **Record Materials:** For critical steps (cutter replacement), record materials used

### Step 12: Record Material Usage

**As materials are used, update ActualBOM records:**

**Location:** Django Admin → Actual BOMs → (Select WO) → Update actual quantities

**Example:**
```
Work Order:         WO-2025-R-0042
BOM Item:           PDC-1308-01 (13mm PDC Cutter)
Planned Quantity:   24
Actual Quantity:    11 (only replaced 11 cutters in this repair)
Lot Number:         LOT-2025-001234
Serial Numbers:     (For critical cutters, record individual serial numbers)
                    SN-001234
                    SN-001235
                    SN-001236
                    ...
Variance Notes:     "Used 11 instead of full 24 due to only gauge cutters damaged.
                     Remaining 13 cutters from original bit still serviceable."
Recorded By:        Ahmed Al-Saudi (operator who installed)
```

---

## Tracking Repair History

### Step 13: Create/Update Repair History Record

**When the repair is complete, create a RepairHistory record:**

**Location:** Django Admin → Repair Histories → Add Repair History

```
Bit Instance:            12345
Work Order:              WO-2025-R-0042
Repair Index:            2 (this is R2)
Evaluation Summary:      EVAL-2025-0012

USAGE BEFORE REPAIR:
Hours on Bit:            450.0
Footage Drilled:         2,800
Damage Description:      "8 cutters broken/missing (gauge row), 3 chipped inner cutters,
                          hardfacing worn 60% on gauge, minor pin thread scoring"

WORK PERFORMED:
Cutters Replaced:        11
Nozzles Replaced:        0
Hardfacing Applied:      ☑ Yes
Threads Repaired:        ☑ Yes
Gauge Repaired:          ☐ No
Balance Check:           ☑ Yes

ROUTING:
Route Template Used:     REPAIR-HEAVY

CHAIN:
Previous Repair:         (Select R1 repair if exists)

COMPLETION:
Repair Completed Date:   2025-11-28
Repair Notes:            "R2 repair completed successfully.

                          WORK DETAILS:
                          - Removed 11 damaged cutters (8 gauge, 3 inner)
                          - Installed 11 new premium PDC cutters (PDC-1308-01)
                          - All cutters brazed and leak-tested (PASS)
                          - Applied tungsten carbide hardfacing to gauge pads
                          - Pin threads dressed, minor scoring removed
                          - Box threads acceptable, no work needed
                          - Re-assembled with new pin seal
                          - Balance check: 0.002" runout (PASS, spec: <0.005")
                          - MPI on all new cutters: PASS
                          - Final QC inspection: APPROVED

                          MATERIALS USED:
                          - 11x PDC-1308-01 cutters (Lot: LOT-2025-001234)
                          - 5 lbs Tungsten Carbide hardfacing
                          - 1x Pin Seal (SEAL-API-4.5)

                          TOTAL HOURS: 14.5 hours (under estimate)

                          READY FOR RELEASE"
```

### Step 14: Update Bit Instance Repair Index

**IMPORTANT:** After completing the repair, update the bit instance:

```
Bit Instance: 12345
Current Repair Index: 2 (was 1, now 2 because this is R2)
```

This ensures the bit will now be displayed as "12345-R2" throughout the system.

---

## Viewing Complete Bit History

### How to View Full History for a Bit

#### Method 1: Via Bit Instance Detail (Recommended)

**Future Enhancement:** Create a custom view showing:
```
Bit Instance: 12345-R2
Design: HD75WF (MAT-001)
Serial: 12345
Current Status: IN_STOCK

┌─────────────────────────────────────────────────────────┐
│ REPAIR HISTORY TIMELINE                                  │
└─────────────────────────────────────────────────────────┘

NEW BUILD (Initial Manufacturing)
  Work Order: WO-2024-M-0034
  Date: 2024-02-15
  Status: COMPLETED
  BOM Used: (show materials)

↓ Released to customer: 2024-02-20

R1 (First Repair)
  Work Order: WO-2024-R-0123
  Received: 2024-08-10
  Hours on Bit: 520
  Footage: 3,200 ft
  Damage: "6 cutters damaged, hardfacing worn"
  Work Done:
    - 6 cutters replaced
    - Hardfacing applied
  Completed: 2024-08-15
  Total Cost: $12,500

↓ Released to customer: 2024-08-18

R2 (Second Repair) ← CURRENT
  Work Order: WO-2025-R-0042
  Received: 2025-11-23
  Hours on Bit: 450
  Footage: 2,800 ft
  Damage: "11 cutters damaged, hardfacing worn, thread scoring"
  Work Done:
    - 11 cutters replaced
    - Hardfacing applied
    - Threads dressed
  Completed: 2025-11-28
  Total Cost: $18,750

┌─────────────────────────────────────────────────────────┐
│ PERFORMANCE SUMMARY                                      │
└─────────────────────────────────────────────────────────┘
Total Hours in Service:  970 hours
Total Footage Drilled:   6,000 ft
Total Repairs:           2
Average Hours per Run:   485 hours
Average Footage per Run: 3,000 ft
Total Repair Cost:       $31,250
```

#### Method 2: Via Django Admin

**Repair History Records:**
Django Admin → Repair Histories → Filter by bit_instance: 12345

**Work Orders:**
Django Admin → Work Orders → Filter by bit_instance: 12345

**Evaluation History:**
Django Admin → Evaluation Summaries → (Search for job cards related to this bit)

---

## Material Usage Tracking

### Viewing Material Variance

**Location:** Django Admin → Actual BOMs → Filter by Work Order

**Variance Report:**
```
Work Order: WO-2025-R-0042

Component: PDC-1308-01 (13mm PDC Cutter)
  Planned:    24 EA
  Actual:     11 EA
  Variance:   -13 EA (13 fewer used than planned)
  Reason:     Only gauge cutters replaced, inner cutters serviceable

Component: NOZ-14-TFA (14/32" Nozzle)
  Planned:    6 EA
  Actual:     0 EA
  Variance:   -6 EA
  Reason:     Nozzles not damaged, reused original

Component: HF-TUNGSTEN (Tungsten Carbide Hardfacing)
  Planned:    5 LB
  Actual:     5 LB
  Variance:   0 LB
  Reason:     Used as planned

Component: SEAL-API-4.5 (API 4.5" Pin Seal)
  Planned:    1 EA
  Actual:     1 EA
  Variance:   0 EA
  Reason:     New seal installed per standard practice
```

### Material Cost Analysis

```python
# Calculate material variance cost
total_planned_cost = sum(
    actualbom.planned_quantity * actualbom.bom_item.unit_cost
    for actualbom in wo.actual_bom.all()
)

total_actual_cost = sum(
    (actualbom.actual_quantity or 0) * actualbom.bom_item.unit_cost
    for actualbom in wo.actual_bom.all()
)

material_savings = total_planned_cost - total_actual_cost
```

---

## Repair Analytics

### Key Metrics to Track

#### 1. Repair Frequency by Bit Design
```sql
SELECT
    design_revision.mat_number,
    COUNT(*) as total_repairs,
    AVG(hours_on_bit) as avg_hours_between_repairs,
    AVG(cutters_replaced) as avg_cutters_per_repair
FROM repair_history
JOIN work_order ON repair_history.work_order_id = work_order.id
JOIN bit_instance ON repair_history.bit_instance_id = bit_instance.id
GROUP BY design_revision.mat_number
ORDER BY total_repairs DESC
```

#### 2. Most Common Failure Modes
```sql
SELECT
    CASE
        WHEN cutters_replaced > 10 THEN 'Heavy Cutter Damage'
        WHEN cutters_replaced BETWEEN 1 AND 10 THEN 'Moderate Cutter Damage'
        WHEN hardfacing_applied = TRUE THEN 'Hardfacing Wear'
        WHEN threads_repaired = TRUE THEN 'Thread Damage'
        WHEN gauge_repaired = TRUE THEN 'Gauge Damage'
    END as failure_mode,
    COUNT(*) as occurrence_count
FROM repair_history
GROUP BY failure_mode
ORDER BY occurrence_count DESC
```

#### 3. Repair Cost Trends
```sql
SELECT
    DATE_TRUNC('month', repair_completed_date) as month,
    COUNT(*) as repairs_completed,
    AVG(cutters_replaced * cutter_unit_cost) as avg_material_cost,
    AVG(estimated_hours * labor_rate) as avg_labor_cost
FROM repair_history
GROUP BY month
ORDER BY month DESC
```

#### 4. Customer-Specific Patterns
```sql
SELECT
    work_order.customer_name,
    COUNT(*) as total_repairs,
    AVG(hours_on_bit) as avg_hours_to_repair,
    AVG(footage_drilled) as avg_footage_to_repair
FROM repair_history
JOIN work_order ON repair_history.work_order_id = work_order.id
GROUP BY work_order.customer_name
ORDER BY total_repairs DESC
```

---

## Best Practices

### 1. Always Check Previous Repairs Before Creating New WO
✅ Review repair_history table
✅ Read previous WO remarks
✅ Check material usage from previous repairs
✅ Look for patterns in damage

### 2. Accurate Material Tracking
✅ Record actual quantities used
✅ Document lot numbers for critical components
✅ Record serial numbers for high-value parts (cutters, bearings)
✅ Explain variances

### 3. Detailed Repair Notes
✅ Document damage observed
✅ Describe work performed
✅ Record any anomalies or special procedures
✅ Include QC results (NDT, balance, etc.)
✅ Note customer feedback if available

### 4. Proper Repair Indexing
✅ Always increment current_repair_index after completing repair
✅ Link to previous_repair for chain tracking
✅ Ensure repair_index matches in RepairHistory and BitInstance

### 5. Evaluation Quality
✅ Thorough evaluation before creating work order
✅ Use RepairDecision to guide routing
✅ Consider previous repair history when evaluating
✅ Document root cause when possible

---

## Troubleshooting

### Problem: Can't find previous repairs for a bit

**Solution:** Check BitInstance record, ensure:
- `serial_number` is correct
- `current_repair_index` has been updated
- RepairHistory records exist and are linked properly

### Problem: BOM quantities don't match

**Solution:**
- Check if BOM was updated after initial WO creation
- Verify ActualBOM records exist for this WO
- Ensure operators are recording actual usage

### Problem: Repair history chain is broken

**Solution:**
- Check `previous_repair` links in RepairHistory
- Ensure repair_index values are sequential
- Manually link if necessary

### Problem: Can't determine which route to use

**Solution:**
1. Create/review RepairDecision record
2. Check evaluation summary
3. Consult with engineering if complex damage
4. Reference similar previous repairs

---

## Summary Workflow Checklist

**For each repair, complete these steps:**

☐ 1. Create BitReceive record
☐ 2. Perform initial inspection
☐ 3. Create EvaluationSummary
☐ 4. Create/review RepairDecision
☐ 5. **Review previous repairs** (via RepairHistory)
☐ 6. **Check previous WO remarks**
☐ 7. **Review BOM from design**
☐ 8. Create repair WorkOrder with detailed remarks
☐ 9. Copy BOM to ActualBOM (planned quantities)
☐ 10. Create JobCard
☐ 11. Generate route steps
☐ 12. Print route sheet with QR codes
☐ 13. Execute repair (operators scan QR codes)
☐ 14. Record actual material usage in ActualBOM
☐ 15. Create/update RepairHistory record
☐ 16. Update BitInstance.current_repair_index
☐ 17. Complete final QC
☐ 18. Create BitRelease record

---

## Database Schema Reference

### Key Models and Relationships

```
BitDesignRevision
  └── BOMItem (1:N) - Components needed for this design

BitInstance
  ├── WorkOrder (1:N) - All work orders for this bit
  ├── RepairHistory (1:N) - Complete repair chain
  └── current_repair_index - Current repair number

WorkOrder
  ├── BitInstance (N:1) - Which bit (for repairs)
  ├── ActualBOM (1:N) - Materials used for this WO
  └── RepairHistory (1:1) - Repair details

EvaluationSummary
  └── RepairDecision (1:1) - Recommended repair actions

RepairHistory
  ├── BitInstance (N:1) - Bit that was repaired
  ├── WorkOrder (1:1) - WO for this repair
  ├── EvaluationSummary (N:1) - Evaluation that triggered repair
  ├── RouteTemplate (N:1) - Route used
  └── previous_repair (N:1) - Link to previous repair in chain
```

---

## API/Code Examples

### Get All Repairs for a Bit

```python
from production.models import BitInstance

bit = BitInstance.objects.get(serial_number="12345")

# Get all repair history in chronological order
repairs = bit.get_repair_history_chain()

for repair in repairs:
    print(f"R{repair.repair_index}: {repair.work_order.wo_number}")
    print(f"  Cutters: {repair.cutters_replaced}")
    print(f"  Hours: {repair.hours_on_bit}")
    print(f"  Notes: {repair.repair_notes}")
```

### Get Last Repair

```python
last_repair = bit.get_last_repair()
if last_repair:
    print(f"Last repair was R{last_repair.repair_index}")
    print(f"Completed: {last_repair.repair_completed_date}")
```

### Check if Bit Can Be Repaired Again

```python
if bit.can_be_repaired_again():
    print(f"Bit can be repaired (currently R{bit.current_repair_index})")
else:
    print("Bit has reached maximum repairs or is scrapped")
```

### Get BOM Variance for a Work Order

```python
from production.models import WorkOrder

wo = WorkOrder.objects.get(wo_number="WO-2025-R-0042")

for actual_bom in wo.actual_bom.all():
    variance = actual_bom.get_variance()
    if variance != 0:
        print(f"{actual_bom.bom_item.part_number}: {variance:+.2f} {actual_bom.bom_item.unit}")
```

---

**For questions or support, contact Production Engineering Department**

