# Intelligent Route Generation System

## Overview

The Production Department now features an **Intelligent Route Generation System** that automatically creates manufacturing route steps based on bit design features, order type, and condition assessment. This eliminates manual route planning and ensures consistency across production.

## How It Works

### Automatic Route Step Generation

When a **Job Card** is created, the system:

1. **Analyzes the bit design**:
   - Bit type (PDC vs Roller Cone)
   - Body material (Matrix vs Steel)
   - Size, blade count, and other features
   - MAT number specifications

2. **Considers the order context**:
   - Order type: NEW_BUILD, REPAIR, or EVALUATION_ONLY
   - Priority level
   - Customer requirements

3. **Selects the appropriate route template**:
   - Matches bit type and body material
   - Filters by order type
   - Chooses most specific template available

4. **Generates route steps automatically**:
   - Creates JobRouteStep instances from template
   - Applies conditional logic (see below)
   - Sets initial status to PENDING

### Conditional Routing Logic

The system intelligently includes or excludes process steps based on several factors:

#### 1. Body Material Logic

**Steel-Body PDC Bits:**
- **SKIP**: Infiltration-related processes
  - MOLD_PREP
  - POWDER_LOADING
  - INFILTRATION
  - COOLING
  - MOLD_REMOVAL
- **INCLUDE**: Machining and finishing processes

**Matrix-Body PDC Bits:**
- **INCLUDE**: Full infiltration workflow
- **INCLUDE**: Post-infiltration machining

#### 2. Order Type Logic

**NEW_BUILD:**
- Includes all applicable manufacturing steps
- Full quality control checkpoints
- Complete process sequence

**REPAIR:**
- Route adjusted based on evaluation (see below)
- May skip heavy manufacturing
- Focus on refurbishment processes

**EVALUATION_ONLY:**
- **ONLY** includes inspection steps:
  - VISUAL_INSPECTION
  - NDT (Non-Destructive Testing)
  - THREAD_INSPECTION
  - DIMENSION_CHECK
  - EVALUATION
  - FINAL_QC

#### 3. Repair Condition Logic

When an **Evaluation Summary** is created for a repair job, the system automatically adjusts the route:

**Minor Damage (MINOR_DAMAGE):**
- **SKIP** heavy processes:
  - INFILTRATION
  - MACHINING
  - MOLD_PREP
  - POWDER_LOADING
  - MAJOR_WELD
- **FOCUS** on:
  - Cleaning
  - Re-brazing
  - Light finishing
  - Inspection

**Major Damage (MAJOR_DAMAGE):**
- **INCLUDE** all rebuild processes
- Similar to new build workflow
- Additional structural repair steps

**Scrap (SCRAP):**
- **CANCEL** all production steps
- **ONLY** retain:
  - EVALUATION
  - SCRAP_DOCUMENTATION
  - FINAL_QC
- Marks other steps as SKIPPED

**OK Condition:**
- Light refurbishment
- Inspection and certification
- Minimal processing

## Usage Examples

### Example 1: New Build Matrix PDC

**Input:**
- Design: HD75WF
- Type: PDC (Fixed Cutter)
- Body Material: MATRIX
- Size: 12.25"
- Order Type: NEW_BUILD

**Generated Route:**
1. MOLD_PREP → Matrix/Infiltration Dept
2. POWDER_LOADING → Matrix/Infiltration Dept
3. INFILTRATION → Matrix/Infiltration Dept
4. COOLING → Matrix/Infiltration Dept
5. MOLD_REMOVAL → Matrix/Infiltration Dept
6. MACHINING → Finishing Dept
7. WELD_UPPER → Assembly Dept
8. BRAZING → Finishing Dept
9. NDT → QC Dept
10. THREAD_INSPECTION → QC Dept
11. FINAL_QC → QC Dept

**Total: 11 steps**

### Example 2: New Build Steel PDC

**Input:**
- Design: SD85BF
- Type: PDC
- Body Material: STEEL
- Size: 8.5"
- Order Type: NEW_BUILD

**Generated Route:**
1. BLANK_PREP → Finishing Dept
2. MACHINING → Finishing Dept
3. WELD_UPPER → Assembly Dept
4. BRAZING → Finishing Dept
5. HEAT_TREATMENT → Finishing Dept
6. NDT → QC Dept
7. THREAD_INSPECTION → QC Dept
8. PAINTING → Finishing Dept
9. FINAL_QC → QC Dept

**Total: 9 steps** (No infiltration!)

### Example 3: Repair with Minor Damage

**Input:**
- Design: HD75WF
- Type: PDC Matrix
- Order Type: REPAIR
- Evaluation: MINOR_DAMAGE

**Generated Route:**
1. EVALUATION → QC Dept
2. CLEANING → Repair Dept
3. INSPECTION → QC Dept
4. RE_BRAZING → Finishing Dept
5. LIGHT_FINISHING → Finishing Dept
6. NDT → QC Dept
7. FINAL_QC → QC Dept

**Total: 7 steps** (Heavy processes skipped!)

### Example 4: Evaluation Only

**Input:**
- Design: Any
- Order Type: EVALUATION_ONLY

**Generated Route:**
1. VISUAL_INSPECTION → QC Dept
2. NDT → QC Dept
3. THREAD_INSPECTION → QC Dept
4. DIMENSION_CHECK → QC Dept
5. EVALUATION → QC Dept
6. FINAL_QC → QC Dept

**Total: 6 steps** (Only inspection!)

## User Interface Features

### Job Card Creation

When creating a job card:
1. Fill in basic information (code, work order, department)
2. Route steps are **automatically generated** upon save
3. No need to manually add route steps!

### Job Card Detail View

The enhanced job card detail page shows:
- **Bit Design Information**: Type, material, size, MAT number
- **Auto-generated Route Steps**: Complete list with status
- **Evaluation Results**: Condition and recommended action
- **Quick Actions** dropdown:
  - Add Evaluation
  - Create NCR
  - Place Hold
  - Regenerate Route

### Route Regeneration

If you need to regenerate routes (after evaluation or design change):
1. Open job card detail
2. Click "Regenerate Route" in Quick Actions
3. Review what will be deleted/kept
4. Confirm regeneration
5. New routes generated based on current data

**Important:** Only PENDING steps are deleted. IN_PROGRESS, DONE, and SKIPPED steps are preserved.

### Evaluation-Triggered Adjustment

When you create an evaluation:
1. Fill out evaluation form
2. Select condition (OK, MINOR_DAMAGE, MAJOR_DAMAGE, SCRAP)
3. Save evaluation
4. **Route automatically adjusts** based on condition
5. Success message confirms adjustment

## Route Template Management

### Creating Route Templates

Route templates are created in Django Admin:

1. Go to Admin → Production → Route Templates
2. Create new template:
   - **Name**: Descriptive (e.g., "PDC Matrix New Build - Standard")
   - **Bit Type**: PDC or ROLLER_CONE
   - **Body Material**: MATRIX, STEEL, or blank
   - **For Order Type**: NEW_BUILD, REPAIR, or EVALUATION_ONLY
   - **Active**: Yes

3. Add Route Step Templates:
   - **Sequence**: Step order (1, 2, 3...)
   - **Process Code**: Unique identifier (e.g., INFILTRATION)
   - **Description**: Detailed instructions
   - **Default Department**: Where this step is performed
   - **Default Workstation**: Specific machine/area
   - **Estimated Duration**: Minutes
   - **Is Mandatory**: Required step?

### Example Template Structure

```
Route Template: "PDC Matrix New Build - Standard"
├── Bit Type: PDC
├── Body Material: MATRIX
├── Order Type: NEW_BUILD
└── Steps:
    1. MOLD_PREP (Matrix/Infiltration, 60 min)
    2. POWDER_LOADING (Matrix/Infiltration, 30 min)
    3. INFILTRATION (Matrix/Infiltration, 480 min)
    4. COOLING (Matrix/Infiltration, 240 min)
    ...
```

## Quality Control Integration

### Non-Conformance Reports (NCR)

When quality issues are detected:
1. Create NCR from job card Quick Actions
2. Form auto-fills job card, work order, bit instance
3. Select severity, disposition, corrective action
4. NCR tracked in quality dashboard

### Production Holds

Place a hold on production:
1. Create hold from job card Quick Actions
2. Select reason (quality, material, customer, etc.)
3. Job card status → QC_HOLD
4. Requires approval for release (optional)

## Benefits

### 1. Consistency
- Same bit type always gets same route
- No human error in route planning
- Standardized processes

### 2. Efficiency
- No manual route step entry
- Instant route generation
- Automatic adjustments

### 3. Flexibility
- Routes adapt to bit features
- Condition-based routing for repairs
- Easy to regenerate if needed

### 4. Quality
- Ensures all required steps included
- Prevents skipping critical processes
- Audit trail of route changes

### 5. Intelligence
- Skips inapplicable processes (e.g., infiltration for steel)
- Adjusts for damage level
- Evaluation-driven workflow

## Technical Details

### Files Involved

- **routing_logic.py**: Core routing intelligence
- **signals.py**: Automatic trigger on job card creation
- **views.py**: Route regeneration views
- **models.py**: JobCard, RouteTemplate, JobRouteStep

### Logging

The system logs all routing decisions:
- Route template selection
- Steps filtered/included
- Automatic adjustments
- Errors and warnings

Check Django logs for debugging.

### Customization

To customize routing logic:
1. Edit `production/routing_logic.py`
2. Modify `_should_include_step()` method
3. Add new conditional rules
4. Test thoroughly!

## Troubleshooting

### No Route Steps Generated

**Possible causes:**
- No matching route template found
- Template is inactive
- Error in routing logic

**Solutions:**
1. Check route templates in admin
2. Verify bit type and body material match
3. Check Django logs for errors
4. Manually regenerate route

### Wrong Steps Generated

**Possible causes:**
- Wrong template selected
- Bit design data incorrect
- Evaluation missing or incorrect

**Solutions:**
1. Verify bit design data
2. Check evaluation results
3. Regenerate route after fixing data

### Steps Not Adjusting After Evaluation

**Possible causes:**
- Signal not firing
- Evaluation created before job card
- Error in adjustment logic

**Solutions:**
1. Manually regenerate route
2. Check Django logs
3. Verify evaluation saved correctly

## Future Enhancements

Planned improvements:
- Size-specific routing (different steps for 6" vs 17.5" bits)
- Customer-specific preferences
- Blade count-based brazing time
- Machine availability routing
- Real-time capacity planning
- AI-based route optimization

## Support

For questions or issues:
1. Check this documentation
2. Review Django admin for templates
3. Check application logs
4. Contact system administrator
