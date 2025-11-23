# Quality Management & Production Controls

## Real-World Production Scenario Handling

This document covers the comprehensive quality and production management features for handling:
- ✅ **Non-Conformances (NCR)**
- ✅ **Material Review Board (MRB) Decisions**
- ✅ **Scrap Tracking**
- ✅ **Rework Management**
- ✅ **Production Holds**

---

## 🔴 Non-Conformance Reports (NCR)

### When to Create an NCR

**Quality Failures**:
- Dimension out of specification (±0.005")
- Surface finish below requirement
- Thread gauge rejection
- NDT failures (cracks, porosity, inclusions)
- Braze quality issues
- Hardfacing defects

**Process Deviations**:
- Infiltration temperature out of range
- Incorrect powder mixture used
- Process step skipped or incomplete
- Wrong material used

**Customer Complaints**:
- Field performance issues
- Damage during shipping
- Missing documentation

### NCR Workflow

```
1. DETECTION
   ├─ Quality inspector detects issue
   ├─ Create NCR with unique number (NCR-2025-001)
   ├─ Severity: MINOR / MAJOR / CRITICAL
   ├─ Status: OPEN
   └─ Link to Job Card / Work Order / Bit Instance

2. INVESTIGATION
   ├─ Status → UNDER_REVIEW
   ├─ Root cause analysis
   ├─ Document corrective action
   └─ Document preventive action

3. MRB DECISION (Material Review Board)
   ├─ Status → PENDING_MRB
   ├─ Engineering review
   ├─ Disposition options:
   │   ├─ USE AS-IS (meets functional requirements)
   │   ├─ USE AS-IS WITH DEVIATION (document waiver)
   │   ├─ REWORK (fix the defect)
   │   ├─ REPAIR (permanent modification)
   │   ├─ SCRAP (cannot be used)
   │   ├─ RETURN TO SUPPLIER (vendor issue)
   │   └─ DOWNGRADE (use for lower specification)
   └─ Record disposition date and decision maker

4. IMPLEMENTATION
   ├─ If REWORK → Create ReworkRecord
   ├─ If SCRAP → Create ScrapRecord
   ├─ If USE AS-IS → Update documentation
   └─ Implement corrective/preventive actions

5. CLOSURE
   ├─ Verify actions completed
   ├─ Status → CLOSED
   ├─ Record closure date and approver
   └─ Update cost impact
```

### NCR Severity Levels

**CRITICAL**:
- Safety hazard
- Complete functional failure
- Customer contract violation
- Regulatory non-compliance
- **Example**: Crack detected in bit body after NDT

**MAJOR**:
- Significant performance impact
- Major rework required
- High cost impact ($5,000+)
- **Example**: Incorrect thread type machined

**MINOR**:
- Cosmetic issues
- Minor rework possible
- Low cost impact (<$1,000)
- **Example**: Surface finish slightly rough but within tolerance

### Real-World Example

**Scenario**: Brazing Quality Issue

```python
# NCR Creation
ncr = NonConformanceReport.objects.create(
    ncr_number='NCR-2025-042',
    job_card=jc,
    severity='MAJOR',
    status='OPEN',
    detected_at_process='BRAZING',
    detected_by='John Smith - QC Inspector',
    description='3 PDC cutters have incomplete braze joints. Visual inspection shows gaps between cutter and bit body. Estimated 20% of braze circumference incomplete.',
    root_cause='Furnace temperature was 50°F below specification due to thermocouple drift. Operator did not verify temperature before loading.',
    corrective_action='Re-braze affected cutters after cleaning joints. Verify temperature with secondary thermometer.',
    preventive_action='Implement daily thermocouple calibration check. Add temperature verification to pre-braze checklist.',
    estimated_cost_impact=3500.00
)

# MRB Decision
ncr.status = 'PENDING_MRB'
ncr.save()

# Engineering reviews and decides
ncr.disposition = 'REWORK'
ncr.disposition_date = timezone.now()
ncr.disposition_by = 'Jane Doe - Chief Engineer'
ncr.disposition_notes = 'Cutters can be safely removed and re-brazed. No damage to bit body. Approve rework per standard procedure RW-BRAZE-001.'
ncr.save()

# Create rework record (see Rework section below)
```

---

## 🔧 Rework Records

### Common Rework Scenarios

**Dimensional Issues**:
- Thread pitch incorrect → Re-cut threads
- OD too large → Additional machining
- Face not perpendicular → Re-face

**Surface/Coating**:
- Hardfacing thickness insufficient → Add material
- Hardfacing has porosity → Remove and reapply
- Surface contamination → Clean and refinish

**Assembly/Brazing**:
- Incomplete braze → Clean and re-braze
- Cutters not flush → Remove and reinstall
- Nozzle misalignment → Remove and reposition

**Infiltration**:
- Incomplete infiltration → Additional furnace cycle (if possible)
- Surface porosity → Fill with braze alloy or scrap

### Rework Workflow

```
1. CREATE REWORK RECORD
   ├─ Rework Number: RW-2025-001
   ├─ Link to NCR (if applicable)
   ├─ Link to Job Card
   ├─ Rework Reason: DIMENSION_OUT_SPEC, INCOMPLETE_BRAZING, etc.
   ├─ Original Process: What went wrong
   ├─ Status: PENDING
   └─ Detailed rework instructions

2. PLAN & ASSIGN
   ├─ Estimate labor hours
   ├─ Estimate material cost
   ├─ Assign to operator
   ├─ Schedule: planned_start, planned_end
   └─ Status → IN_PROGRESS

3. EXECUTE REWORK
   ├─ Operator performs rework
   ├─ Record actual_start, actual_end
   ├─ Update labor_hours
   └─ Update material_cost

4. VERIFY
   ├─ QC inspector verifies rework
   ├─ Record verified_by, verified_date
   ├─ Verification notes (measurements, test results)
   └─ Status → COMPLETED or FAILED

5. OUTCOMES
   ├─ COMPLETED → Job card continues
   ├─ FAILED → Create new NCR, likely SCRAP
   └─ Update total_cost
```

### Cost Tracking

**Labor Hours**: Track actual time spent
**Material Cost**: Additional cutters, braze alloy, hardfacing material
**Total Cost**: Labor + Material = Total rework impact

**Example**:
```python
rework = ReworkRecord.objects.create(
    rework_number='RW-2025-013',
    job_card=jc,
    ncr=ncr,  # Link to NCR
    rework_reason='INCOMPLETE_BRAZING',
    original_process='BRAZING',
    rework_description='3 PDC cutters with incomplete braze (see NCR-2025-042)',
    rework_instructions='''
    1. Remove affected cutters using heat lance
    2. Clean braze surfaces with wire brush
    3. Inspect pockets for damage
    4. Re-braze cutters per SOP-BRAZE-001
    5. Verify temperature: 1850°F ± 25°F
    6. Cool slowly (4 hours minimum)
    7. Visual inspection: 100% braze contact
    8. Re-do NDT (MPI on braze joints)
    ''',
    status='PENDING',
    assigned_to_name='Mike Johnson',
    labor_hours=6.5,
    material_cost=450.00,  # 3 cutters @ $150 each
    total_cost=1250.00  # Labor (6.5h @ $123/h) + material
)
```

---

## 🗑️ Scrap Records

### When to Scrap

**Quality Failures**:
- Cracks detected (NDT)
- Material defects (porosity, inclusions)
- Excessive wear (repair not economical)
- Braze failure (cannot be re-brazed)

**Manufacturing Errors**:
- Wrong material used
- Incorrect design machined
- Damage during processing
- Infiltration complete failure

**Economic Decisions**:
- Rework cost > 60% of new bit cost
- Multiple rework attempts failed
- Customer rejected (cannot be sold)

**Design/Business**:
- Design obsolete (no longer manufactured)
- Customer order cancelled
- Inventory obsolescence

### Scrap Workflow

```
1. SCRAP DECISION
   ├─ Determine if item is scrappable
   ├─ Check if rework is economical
   ├─ Get supervisor approval
   └─ Create Scrap Record

2. DOCUMENTATION
   ├─ Scrap Number: SCRAP-2025-001
   ├─ Scrap Reason: QUALITY_FAILURE, MFG_ERROR, etc.
   ├─ Item Description: "Complete 12.25" PDC bit, Serial 20250042"
   ├─ Quantity and Unit
   └─ Link to Bit Instance, Job Card, NCR

3. COST TRACKING
   ├─ Material Cost: Raw materials invested
   │   ├─ Bit body: $8,000
   │   ├─ PDC cutters (48x @ $150): $7,200
   │   ├─ Nozzles, pins, etc.: $500
   │   └─ Total material: $15,700
   ├─ Labor Cost: Hours invested
   │   ├─ Infiltration: 12h @ $85/h = $1,020
   │   ├─ Machining: 8h @ $95/h = $760
   │   ├─ Brazing: 6h @ $110/h = $660
   │   └─ Total labor: $2,440
   └─ Total Cost: $18,140

4. APPROVAL
   ├─ Supervisor/Manager approval required
   ├─ Record approved_by and approval_date
   └─ For high-value items (>$10k), may require upper management

5. SALVAGE/RECOVERY
   ├─ Can PDC cutters be salvaged? → Salvage value
   ├─ Can matrix body be recycled? → Metal recovery value
   ├─ Record salvage_value
   └─ Record salvage_notes
   
6. UPDATE STATUS
   ├─ If Bit Instance → Set status to SCRAPPED
   ├─ Close related NCR
   └─ Update job card status
```

### Scrap Reasons (Detailed)

**QUALITY_FAILURE**
- Failed final inspection
- Customer rejection after delivery
- Field failure analysis shows manufacturing defect

**MATERIAL_DEFECT**
- Powder contamination in matrix body
- Steel forging has internal defects
- PDC cutters have cracks

**INFILTRATION_FAILURE**
- Incomplete infiltration (voids, porosity)
- Infiltration cracking
- Wrong alloy used
- Temperature profile deviation caused defects

**BRAZE_FAILURE**
- Complete braze failure (cutters falling out)
- Multiple rework attempts failed
- Thermal damage to bit body during braze

**CRACK_DETECTED**
- NDT (MPI, UT) found cracks
- Thermal cracks from welding/brazing
- Fatigue cracks during testing

**Example**:
```python
scrap = ScrapRecord.objects.create(
    scrap_number='SCRAP-2025-008',
    bit_instance=bit,
    job_card=jc,
    ncr=ncr,
    scrap_reason='CRACK_DETECTED',
    item_description='Complete 12.25" Matrix PDC bit, Serial 20250042',
    quantity=1.0,
    unit='EA',
    material_cost=15700.00,
    labor_cost=2440.00,
    total_cost=18140.00,
    approved_by='Sarah Williams - Production Manager',
    approval_date=timezone.now(),
    salvage_value=3600.00,  # 24 cutters salvageable @ $150 each
    salvage_notes='24 of 48 PDC cutters removed and cleaned for reuse. Matrix body recycled for tungsten recovery (estimated $1,200 value). Total salvage: $4,800.',
    remarks='Thermal crack detected during MPI after final braze. Crack extends 2.5" into bit body. Engineering determined crack likely occurred during infiltration due to cooling too quickly. Preventive action: Update cooling procedure to minimum 8 hours.'
)

# Update bit instance
bit.status = 'SCRAPPED'
bit.save()
```

---

## ⏸️ Production Holds

### Hold Reasons (Detailed)

**WAITING_MATERIAL**
- PDC cutters not received from supplier
- Hardfacing wire out of stock
- Powder mixture not available
- Steel forgings delayed

**WAITING_QC**
- Awaiting NDT inspection results
- Thread gauges being calibrated
- Lab analysis of material properties
- Third-party certification pending

**WAITING_ENGINEERING**
- Design change pending approval
- Customer requested modification
- Engineering investigating quality issue
- Drawing revision not released

**MACHINE_BREAKDOWN**
- CNC machine down for repair
- Infiltration furnace malfunction
- Brazing furnace needs maintenance
- Thread cutting machine broken

**CUSTOMER_HOLD**
- Customer requested production pause
- Order cancelled/modified
- Awaiting customer specification
- Payment issue

**QUALITY_ISSUE**
- Investigating NCR before proceeding
- Awaiting MRB decision
- Previous batch had issues, holding all similar work
- Root cause analysis in progress

### Hold Workflow with Approval

```
1. INITIATE HOLD
   ├─ Create ProductionHold record
   ├─ Hold Number: HOLD-2025-015
   ├─ Hold Reason: QUALITY_ISSUE, CUSTOMER_HOLD, etc.
   ├─ hold_initiated_by: Name of person placing hold
   ├─ hold_start: Timestamp
   ├─ Status: ACTIVE
   └─ Update Job Card status to QC_HOLD

2. DOCUMENT IMPACT
   ├─ Description: Detailed reason for hold
   ├─ estimated_delay_hours: Impact on schedule
   ├─ cost_impact: Financial impact
   └─ Link to Work Order for customer visibility

3. APPROVAL REQUIREMENT (if needed)
   ├─ requires_approval = True (for customer holds, design changes)
   ├─ Hold remains ACTIVE until approved
   ├─ Cannot release without management approval
   └─ Escalation for long-duration holds (>48h)

4. RELEASE HOLD
   ├─ Document resolution
   ├─ If requires_approval:
   │   ├─ Get approval from manager/customer
   │   ├─ Record approved_for_release_by
   │   └─ Record approval_date
   ├─ Set hold_end timestamp
   ├─ Status → RELEASED
   ├─ Calculate actual duration
   └─ Update Job Card status to continue production

5. OR CANCEL
   ├─ If work order cancelled
   ├─ Status → CANCELLED
   └─ Document reason
```

### Example: Customer Hold with Approval

```python
hold = ProductionHold.objects.create(
    hold_number='HOLD-2025-027',
    job_card=jc,
    work_order=wo,
    hold_reason='CUSTOMER_HOLD',
    hold_initiated_by='Customer Service - Jane Doe',
    description='Customer (Halliburton) requested hold on all PDC bits for Rig-42. Customer is re-evaluating formation data and may change bit specification from 12.25" to 14.75". Awaiting customer decision by 2025-12-15.',
    requires_approval=True,  # Requires approval to release
    estimated_delay_hours=120.0,  # 5 days
    cost_impact=2500.00,  # Holding costs, schedule impact
    status='ACTIVE'
)

# Later, when customer confirms to proceed...
hold.resolution = 'Customer confirmed to proceed with original 12.25" specification. No design changes required. Proceed with production as planned.'
hold.approved_for_release_by='Sales Manager - Bob Smith'
hold.approval_date = timezone.now()
hold.hold_end = timezone.now()
hold.status = 'RELEASED'
hold.save()

# Update job card to continue
jc.status = 'IN_PROGRESS'
jc.save()
```

---

## 📊 Cost Impact Summary

### Total Quality Cost Formula

```
Total Quality Cost = 
    Σ(NCR costs) + 
    Σ(Rework costs) + 
    Σ(Scrap costs - Salvage value) + 
    Σ(Hold costs)
```

### Reporting Metrics

**By NCR**:
- NCRs per month
- NCRs by severity (Critical/Major/Minor)
- NCRs by process (Brazing, Infiltration, Machining)
- Average time to close NCR
- Disposition breakdown (Scrap vs Rework vs Use As-Is)

**By Scrap**:
- Total scrap cost per month
- Scrap by reason code
- Scrap rate (% of total production)
- Salvage recovery rate
- Top scrap contributors (process/operator)

**By Rework**:
- Rework hours per month
- Rework cost per month
- Rework by reason code
- Average rework attempts before success/scrap
- First-pass yield (% without rework)

**By Hold**:
- Total hold hours per month
- Hold by reason code
- Average hold duration
- Holds requiring approval
- Cost impact of holds

---

## 🎯 Best Practices

### Preventive Actions

1. **Trend Analysis**: Review NCRs monthly for patterns
2. **Root Cause**: Always complete root cause analysis
3. **Preventive Actions**: Implement to prevent recurrence
4. **Training**: Address operator skill gaps
5. **Process Improvement**: Update SOPs based on lessons learned

### Cost Control

1. **Quick Decisions**: Don't delay MRB decisions (holding costs add up)
2. **Salvage**: Always try to recover value from scrap
3. **Rework Economics**: If rework > 60% of new cost, consider scrap
4. **Hold Minimization**: Proactively address hold reasons

### Documentation

1. **Detailed NCRs**: Future reference for similar issues
2. **Photos**: Document defects visually
3. **Cost Tracking**: Accurate costs for decision-making
4. **Approval Trail**: Clear accountability

---

## 📈 Dashboard Integration

The production dashboard shows:
- ✅ **Active NCRs** (Open, Under Review, Pending MRB)
- ✅ **Jobs on QC Hold** (with hold reasons)
- ✅ **Rework in Progress** (count and estimated completion)
- ✅ **Monthly Scrap Cost** (with trend vs last month)
- ✅ **Active Production Holds** (count and total delay hours)

---

## 🔗 Integration with Existing Models

**NCR** ↔ **Job Card**: Track where issue detected
**NCR** ↔ **Bit Instance**: Track bit history with NCRs
**NCR** ↔ **Rework Record**: Link rework to originating NCR
**NCR** ↔ **Scrap Record**: Link scrap decisions
**Production Hold** ↔ **Job Card**: Automatic status update to QC_HOLD
**Scrap** ↔ **Bit Instance**: Update status to SCRAPPED

---

**This comprehensive quality management system ensures full traceability, accountability, and cost tracking for all production issues!**
