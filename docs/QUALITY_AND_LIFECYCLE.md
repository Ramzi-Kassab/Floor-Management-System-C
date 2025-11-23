

# Quality Control & Item Lifecycle Management

Complete guide for handling defective items, expiry tracking, second-hand items, and quality inspections.

## Table of Contents
1. [Overview](#overview)
2. [Quality Inspection Process](#quality-inspection-process)
3. [Defective Items Management](#defective-items-management)
4. [Expiry Tracking & Management](#expiry-tracking--management)
5. [Second-Hand / Used Items](#second-hand--used-items)
6. [Batch & Lot Tracking](#batch--lot-tracking)
7. [Cost Recovery](#cost-recovery)
8. [Reports & Analytics](#reports--analytics)

---

## Overview

The Quality & Lifecycle Management system provides comprehensive tools for:
- **Quality Control**: Inspect items during receiving and in-process
- **Defect Management**: Track, analyze, and dispose of defective items
- **Expiry Management**: FEFO recommendations, expiry alerts, disposal workflows
- **Used Items**: Track condition, maintenance, and lifecycle of reused items
- **Batch Tracking**: Manage batches with expiry dates and certificates

**Access**: Inventory → Quality & Lifecycle Management

---

## Quality Inspection Process

### When to Inspect

| Inspection Type | Trigger | Purpose |
|----------------|---------|---------|
| **Receiving Inspection** | Items received from supplier | Verify quality before accepting |
| **In-Process** | During manufacturing/assembly | Catch defects early |
| **Final Inspection** | Before delivery to customer | Ensure quality standards |
| **Periodic** | Scheduled intervals | Verify stored items |
| **Customer Return** | Items returned by customer | Assess for credit/rework |

### Inspection Results

```
PASS ✓
  └─> Accept items
  └─> Move to approved location
  └─> Available for use

CONDITIONAL PASS ⚠️
  └─> Accept with minor issues noted
  └─> Use with restrictions

REWORK 🔧
  └─> Send to rework location
  └─> Track repair costs
  └─> Re-inspect after rework

REJECT ❌
  └─> Create return to vendor
  └─> Or downgrade for discount sale

SCRAP 🗑️
  └─> Dispose/destroy
  └─> Record loss
  └─> Update inventory
```

### Inspection Workflow

```
1. Receive items from GRN
2. Create Quality Inspection record
3. Inspector examines items
4. Document defects (photos, description)
5. Record quantities:
   - Accepted
   - Rejected
   - For rework
6. Assign defect category and severity
7. Save inspection result
8. System triggers disposition workflow
```

---

## Defective Items Management

### Defect Categories

| Category | Examples | Severity Levels |
|----------|----------|----------------|
| **Dimensional** | Wrong size, out of tolerance | CRITICAL if safety impact |
| **Visual** | Scratches, discoloration, finish | Usually MINOR |
| **Functional** | Doesn't work, performance issues | CRITICAL/MAJOR |
| **Material** | Wrong material, composition | CRITICAL |

### Disposition Options

#### 1. Return to Vendor
```
✓ When to use: Vendor fault, wrong item, defective on arrival
✓ Process:
  - Create goods return (RTV)
  - Link to quality inspection
  - Get RMA from supplier
  - Deduct from stock
  - Track credit note
```

#### 2. Rework/Repair
```
✓ When to use: Item can be fixed economically
✓ Process:
  - Move to rework location
  - Track rework costs
  - Assign to technician
  - Re-inspect after repair
  - If passes → Return to stock
  - If fails → Scrap
```

#### 3. Scrap/Dispose
```
✓ When to use: Irreparable, unsafe, contaminated
✓ Process:
  - Create disposal record
  - Get supervisor approval
  - Execute disposal
  - Record loss amount
  - Remove from inventory
```

#### 4. Downgrade to Second Grade
```
✓ When to use: Defects don't affect function, only aesthetics
✓ Process:
  - Assess market value for second-grade
  - Change condition to USED
  - Update pricing (50-70% of original)
  - Sell at discount
  - Track recovery value
```

#### 5. Use As-Is (Concession)
```
✓ When to use: Minor defects, customer accepts
✓ Process:
  - Get quality manager approval
  - Document concession
  - Mark items accordingly
  - Inform customer if needed
```

### Cost Tracking

```python
Defect Cost Analysis:
  Original Value:     $10,000
  Recovery Options:
    - Rework cost:    $   500  → Recovery: $ 9,500 (Net: $ 9,000)
    - Scrap value:    $ 1,000  → Loss:     $ 9,000
    - Downgrade:      $ 6,000  → Loss:     $ 4,000
    - Return credit:  $10,000  → Loss:     $     0

  Best Option: Return to vendor (if vendor fault)
  Second Best: Downgrade (if usable with defects)
```

---

## Expiry Tracking & Management

### Items That Expire

- **Chemicals & Adhesives**: Matrix powders, hardfacing materials
- **Consumables**: Oils, greases, fluids
- **Safety Equipment**: Protective gear, first aid supplies
- **Calibration Certificates**: Testing equipment certification
- **Batched Items**: Anything with lot/batch numbers

### Expiry Alerts

| Alert Level | Trigger | Action Required |
|------------|---------|----------------|
| 🟢 **Green** | > 30 days | No action |
| 🟡 **Yellow** | 7-30 days | Prioritize usage (FEFO) |
| 🟠 **Orange** | 1-7 days | Use immediately or dispose |
| 🔴 **Red** | Expired | Stop use, initiate disposal |

### FEFO (First Expired First Out)

System automatically recommends which batches to use first:

```
Item: MATRIX-POWDER-A
Available Batches:
  1. Batch-001: Expires 2025-12-15 (45 days) ← USE FIRST ✓
  2. Batch-002: Expires 2026-01-20 (81 days)
  3. Batch-003: Expires 2026-03-10 (130 days)

Recommendation: Issue from Batch-001 first
```

### Expired Item Disposal Workflow

```
1. System alerts: "Batch-001 expired on 2025-11-15"
2. Warehouse checks physical stock
3. Create Expired Item Action:
   - Action Type: DISPOSE / WRITE_OFF / RETURN / DONATE
   - Quantity: 50 KG
   - Book Value: $2,500
   - Recovery Value: $0 (if disposal)
   - Loss: $2,500
4. Submit for approval
5. Supervisor approves
6. Execute disposal
7. Record certificate number
8. Write off from accounts
9. Remove from inventory
```

### Preventing Expiry

**Best Practices**:
- Order smaller quantities more frequently
- Monitor expiry dashboard weekly
- Rotate stock (FEFO)
- Negotiate return policies for near-expiry items
- Track usage patterns to avoid over-ordering

---

## Second-Hand / Used Items

### Condition Grading System

| Grade | Description | Typical Value | Usage |
|-------|-------------|---------------|-------|
| **A** | Excellent - Like new | 85-95% | Minimal use, pristine condition |
| **B** | Good - Minor wear | 70-85% | Light use, fully functional |
| **C** | Fair - Visible wear | 50-70% | Moderate use, some cosmetic issues |
| **D** | Poor - Significant wear | 30-50% | Heavy use, consider retirement |
| **R** | Refurbished | 60-80% | Restored to good condition |

### Tracking Requirements

For each used item, track:
- ✓ **Serial Number**: Unique identifier
- ✓ **Condition Grade**: A/B/C/D/R
- ✓ **Usage Hours**: Total hours of operation
- ✓ **Usage Cycles**: Number of uses (for tools)
- ✓ **Maintenance History**: Last service, next due date
- ✓ **Warranty**: Expiry date, terms
- ✓ **Current User**: Who has it
- ✓ **Serviceability**: Working or not

### Maintenance Scheduling

```
Equipment: DRILL-MOTOR-001
Usage Hours: 450 hours
Maintenance Intervals: Every 500 hours

Schedule:
  Last Maintenance:   2025-10-01 (at 250 hrs)
  Next Maintenance:   2025-12-15 (at 500 hrs)
  Status:            ⚠️ DUE SOON (50 hrs remaining)

Actions:
  - Schedule maintenance appointment
  - Order required parts
  - Remove from service when due
  - Complete maintenance
  - Update tracking record
```

### Lifecycle Management

```
New Item Purchase → Use → Grade A
  ↓
Light use (500 hrs) → Grade B
  ↓
Moderate use (1500 hrs) → Grade C
  ↓ Maintenance due
Refurbishment → Grade R
  ↓
Continue use (2500 hrs) → Grade D
  ↓
Decision Point:
  - If repairable → Refurbish again
  - If costly → Retire/Sell
  - If unsafe → Scrap
```

---

## Batch & Lot Tracking

### Why Track Batches?

- **Expiry Management**: Know which batches expire when
- **Quality Traceability**: Track back to supplier batch
- **Recall Management**: Isolate affected batches
- **Certificate Tracking**: Link quality certificates
- **FEFO Enforcement**: Use oldest batches first

### Batch Information

```
Batch Number: BATCH-2025-001
Item: MATRIX-POWDER-A
Manufacturing Date: 2025-01-15
Expiry Date: 2026-01-15
Shelf Life: 365 days

Supplier Info:
  Supplier: ABC Materials Inc.
  Supplier Batch: SUP-BATCH-12345
  Certificate No: CERT-2025-0123
  Certificate URL: https://...

Status:
  Quarantined: No
  Expired: No
  Recalled: No

Current Stock in Batch: 125.5 KG
Locations:
  - POWDER-SILO-1: 100 KG
  - POWDER-SILO-2: 25.5 KG
```

### Quarantine Management

Items placed in quarantine:
- Pending quality inspection
- Awaiting certificate verification
- Under investigation
- Supplier recall issued

```
Quarantined items cannot be:
  ❌ Issued for production
  ❌ Transferred to regular locations
  ❌ Sold to customers

Quarantined items can be:
  ✓ Inspected
  ✓ Tested
  ✓ Released (after approval)
  ✓ Rejected and returned
```

---

## Cost Recovery

### Maximizing Recovery from Defects

| Scenario | Typical Recovery | Best Practice |
|----------|-----------------|---------------|
| **Vendor Fault** | 100% (credit) | Return immediately with QC report |
| **Rework** | 90-95% | If repair cost < 20% of value |
| **Downgrade** | 50-70% | Sell as second grade instead of scrap |
| **Scrap Metal** | 10-20% | Sell for scrap value |
| **Disposal** | 0% | Last resort, total loss |

### Example Recovery Calculation

```
Scenario: 100 units of Item-A received, 20 defective

Original Cost per unit: $100
Total investment: 100 × $100 = $10,000

Options Analysis:

1. Return All Defective to Vendor
   Quantity: 20 units
   Credit: 20 × $100 = $2,000
   Loss: $0
   Recovery Rate: 100%

2. Rework Defective
   Rework cost per unit: $15
   Total rework: 20 × $15 = $300
   Units salvaged: 20
   Value recovered: $2,000 - $300 = $1,700
   Recovery Rate: 85%

3. Sell as Second Grade
   Selling price: $60 each
   Revenue: 20 × $60 = $1,200
   Loss: $2,000 - $1,200 = $800
   Recovery Rate: 60%

4. Scrap
   Scrap value: $5 each
   Revenue: 20 × $5 = $100
   Loss: $2,000 - $100 = $1,900
   Recovery Rate: 5%

Recommendation: Return to vendor (Option 1)
If vendor won't accept: Rework (Option 2)
```

---

## Reports & Analytics

### Quality Metrics Dashboard

```
Inspection Performance (Last 30 Days):
  Total Inspections: 150
  Pass: 127 (85%)
  Conditional: 8 (5%)
  Rework: 10 (7%)
  Reject: 5 (3%)

Pass Rate Trend:
  This month: 85%
  Last month: 82%
  Improvement: +3% ✓
```

### Defect Analysis

**Top Defect Categories**:
1. Dimensional (45%)
2. Visual (30%)
3. Functional (15%)
4. Material (10%)

**Top Defective Items**:
1. CUTTER-TYPE-A: 12 failures
2. STEEL-BODY-B: 8 failures
3. MATRIX-POWDER-C: 6 failures

**Supplier Quality Ranking**:
| Supplier | Inspections | Pass Rate | Reject Rate |
|----------|-------------|-----------|-------------|
| ABC Materials | 50 | 96% 🟢 | 4% |
| XYZ Corp | 40 | 85% 🟡 | 15% |
| DEF Ltd | 30 | 72% 🔴 | 28% |

**Action**: Review quality with DEF Ltd, consider alternative suppliers

### Expiry Report

```
Items Expiring Next 30 Days:
  Item                  Batch         Qty    Expires      Days Left
  -------------------------------------------------------------------
  MATRIX-POWDER-A      BATCH-001     50 KG  2025-12-05   2 days  🔴
  HARDFACING-B         BATCH-023     25 KG  2025-12-12   9 days  🟠
  ADHESIVE-C           BATCH-045     10 L   2025-12-28   25 days 🟡

Expired Items (Action Required):
  GREASE-TYPE-A        BATCH-018     15 L   2025-11-20   ❌ EXPIRED
  Action: Dispose and write off
```

### Used Items Report

```
Maintenance Overdue:
  Equipment           Serial No    Last Service  Days Overdue
  ----------------------------------------------------------
  DRILL-001          SN-12345     2025-09-01    62 days 🔴
  GRINDER-002        SN-23456     2025-10-15    18 days 🟠

Warranty Expiring:
  Equipment           Warranty Expires    Value
  ----------------------------------------------
  WELDER-A           2025-12-15          $5,500
  PRESS-B            2025-12-30          $8,200

Recommendation: Schedule maintenance before warranty expires
```

---

## Best Practices

### Quality Control
1. ✓ Inspect ALL items during receiving
2. ✓ Document defects with photos
3. ✓ Track defect patterns by supplier
4. ✓ Hold supplier quarterly reviews
5. ✓ Maintain calibrated inspection equipment

### Expiry Management
1. ✓ Set alerts 30 days before expiry
2. ✓ Implement strict FEFO
3. ✓ Train staff on expiry importance
4. ✓ Review slow-moving items monthly
5. ✓ Order smaller quantities more frequently

### Used Items
1. ✓ Assign unique serial numbers
2. ✓ Photo document condition
3. ✓ Schedule preventive maintenance
4. ✓ Track total cost of ownership
5. ✓ Retire at Grade D or safety concern

### Cost Recovery
1. ✓ Always attempt vendor credit first
2. ✓ Consider rework if < 20% of value
3. ✓ Sell as second grade before scrapping
4. ✓ Track recovery rates by category
5. ✓ Set recovery targets (aim for >60%)

---

## System Configuration

### Email Alerts
Configure in settings.py:
```python
QUALITY_ALERT_EMAILS = [
    'quality.manager@company.com',
    'warehouse.supervisor@company.com',
]

EXPIRY_ALERT_DAYS = 30  # Alert when expiry < 30 days
MAINTENANCE_ALERT_DAYS = 7  # Alert when maintenance due < 7 days
```

### Approval Thresholds
```python
QUALITY_APPROVAL_REQUIRED = {
    'disposition_scrap': True,  # Always require approval for scrap
    'write_off_amount': 1000,   # Require approval if write-off > $1000
    'downgrade_grade_c': True,  # Require approval for Grade C or worse
}
```

### Batch Tracking
```python
BATCH_TRACKING_REQUIRED = [
    'MATRIX_POWDER',
    'HARDFACING',
    'CONSUMABLE',
]

EXPIRY_TRACKING_REQUIRED = [
    'MATRIX_POWDER',
    'HARDFACING',
    'CONSUMABLE',
]
```

---

## Troubleshooting

**Q: Items show as expired but are still usable**
A: Check if shelf life was calculated incorrectly. Review manufacturing vs expiry dates.

**Q: Can't find batch number on received items**
A: Contact supplier for batch documentation. All batched items must have traceable batch numbers.

**Q: Rework cost exceeds item value**
A: Change disposition to SCRAP or RETURN. Document reason for financial review.

**Q: Defect patterns from specific supplier**
A: Generate supplier quality report. Schedule review meeting. Consider alternative suppliers.

**Q: Too many expired items**
A: Review ordering patterns. Implement FEFO strictly. Reduce order quantities. Increase order frequency.

---

## Quick Reference

### Access Points
- Quality Dashboard: `Inventory → Quality & Lifecycle`
- Expiry Management: `Inventory → Quality → Expiry Dashboard`
- Defective Items: `Inventory → Quality → Defective Items`
- Used Items: `Inventory → Quality → Used Items`

### Common Actions
- Create Inspection: From GRN detail page
- Dispose Expired: `Expiry Dashboard → Create Action`
- Track Used Item: `Used Items → Add New`
- Generate Reports: `Quality → Reports`

### Support
- Documentation: `/docs/QUALITY_AND_LIFECYCLE.md`
- Training Videos: (link to training materials)
- Contact: quality@company.com
