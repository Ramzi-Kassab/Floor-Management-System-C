# Production Department - Drilling Bits Manufacturing System

## Overview

A comprehensive Django-based Production Department management system for a drilling bits factory that manufactures and repairs PDC (Fixed Cutter) and Roller Cone drilling bits.

## System Features

### Core Functionality

**Bit Management**
- **Bit Designs**: Engineering blueprints with design codes (e.g., HD75WF)
- **Bit Design Revisions**: MAT numbers (Level 3/4/5) tracking engineering changes
- **Bit Instances**: Physical bits with serial numbers tracking through manufacturing, sales, and repairs (12345678-R1, R2, etc.)

**Manufacturing Types**
- Matrix-body PDC: Produced via infiltration furnace in Matrix/Infiltration Department
- Steel-body PDC: Machined steel bodies (internal or JV semi-finished)
- Roller Cone: Assembly and finishing
- Repair workflows: R1, R2, R3+ for returned bits

**Work Orders & Job Cards**
- Work Orders: High-level manufacturing/repair orders with customer information
- Job Cards: Shop floor execution cards with QR code support
- Department routing: Matrix/Infiltration → Finishing → QC

**Infiltration Department**
- Batch production tracking for matrix bodies
- Furnace management (temperature profiles, cycles)
- Mold and powder mixture tracking
- Integration with job cards

**Quality Control**
- Evaluation summaries for returned bits
- NDT (Non-Destructive Testing): MPI, DPI, UT, RT, VT
- Thread inspection (API, premium connections)
- Damage mapping and condition assessment

**Routing System**
- Predefined route templates for different bit types and operations
- Step-by-step process tracking (INFILTRATION, MACHINING, BRAZING, etc.)
- Department and workstation assignment
- Operator tracking and timing

**QR Code Integration**
- Auto-generated QR codes for job cards
- Shop floor scanning for quick access
- Mobile-friendly workflows

## Architecture

### Models (15 Core Models)

**Bit Design & Instances**
- `BitDesign`: Core design/blueprint
- `BitDesignRevision`: MAT numbers and versioning  
- `BitInstance`: Physical bits with serial numbers

**Work Orders & Job Cards**
- `WorkOrder`: Manufacturing/repair orders
- `JobCard`: Shop floor execution cards
- `JobPause`: Track work holds/delays

**Routing & Execution**
- `RouteTemplate`: Predefined workflows
- `RouteStepTemplate`: Steps within routes
- `JobRouteStep`: Actual step execution

**Infiltration (Matrix Production)**
- `InfiltrationBatch`: Furnace batch management
- `InfiltrationBatchItem`: Individual items in batches

**Quality Control**
- `EvaluationSummary`: Overall bit assessment
- `NDTResult`: Non-destructive testing
- `ThreadInspectionResult`: Thread QC

**QR Codes**
- `QRCode`: Shop floor tracking

### Key Choices/Enums

```python
BitType: PDC, ROLLER_CONE
BodyMaterial: MATRIX, STEEL
ManufacturingSource: INTERNAL_MATRIX, INTERNAL_STEEL, JV_PARTIAL
OrderType: NEW_BUILD, REPAIR, EVALUATION_ONLY
Department: MATRIX_INFILTRATION, FINISHING, REPAIR, QC, ASSEMBLY
InfiltrationBatchStatus: PLANNED, LOADING, IN_FURNACE, COOLING, COMPLETED, ABORTED
```

## Manufacturing Workflows

### Matrix-body PDC New Build

1. **Matrix/Infiltration Department**
   - Mold preparation & cleaning
   - Powder loading & insert placement
   - Binder/alloy positioning
   - Furnace cycle (temperature profile)
   - Cooling & demolding
   - Transfer to Finishing

2. **Finishing Department**
   - Post-infiltration machining
   - Weld upper API connector
   - Brazing PDC cutters
   - Final finishing
   - NDT & thread inspection
   - Final QC

### Steel-body PDC New Build

1. Steel body procurement (internal or JV partial)
2. **Finishing Department**
   - Machining
   - Weld upper section (if needed)
   - Hardfacing/protection
   - Brazing cutters
   - NDT & thread inspection
   - Final QC

### Repair Workflow

1. **Receiving**
   - Washing & cleaning
   - Visual inspection

2. **Evaluation** (`EvaluationSummary`)
   - Damage mapping
   - Condition assessment: OK, Minor Damage, Major Damage, Scrap
   - Recommended action: Return As-Is, Repair, Scrap

3. **Repair** (if recommended)
   - Body rebuilding (matrix or steel)
   - Hardfacing/overlay
   - Cutter replacement
   - Balancing (roller cones)
   - NDT & thread inspection
   - Final QC

4. **Bit Update**
   - Increment `current_repair_index` (0→1→2→3...)
   - Serial displays as "12345678-R1", "12345678-R2", etc.

## URLs & Views

```
/production/                          Dashboard
/production/workorders/               Work order list
/production/workorders/<id>/          Work order detail
/production/workorders/create/        Create work order
/production/jobcards/                 Job card list
/production/jobcards/<id>/            Job card detail
/production/jobcards/<id>/qr/         Generate QR code (PNG)
/production/qr/<code>/                Scan QR code (redirect)
/production/designs/                  Bit design list
/production/instances/                Bit instance list
/production/infiltration/             Infiltration batch list
/production/routes/                   Route template list
```

## Admin Interface

Comprehensive Django admin for all models with:
- List displays with filters and search
- Date hierarchies for temporal data
- Inlines for related objects (e.g., route steps, batch items)
- Autocomplete fields for foreign keys
- Custom actions and calculated fields

## Templates

All templates use Bootstrap 5 with:
- Responsive design
- Consistent navigation
- Django messages integration
- Form styling with django-widget-tweaks
- Pagination support
- Search and filter forms

## Setup & Installation

### Requirements
```bash
pip install -r requirements.txt
```

Key dependencies:
- Django 5.2.6
- PostgreSQL (psycopg2-binary)
- django-widget-tweaks
- qrcode
- Pillow

### Database Setup
```bash
python manage.py makemigrations production
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run Development Server
```bash
python manage.py runserver
```

Access:
- Application: http://localhost:8000/production/
- Admin: http://localhost:8000/admin/
- Login: http://localhost:8000/accounts/login/

## Usage Examples

### Creating a New Matrix-body PDC Bit

1. **Create Bit Design** (if new)
   - Design code: HD75WF
   - Type: PDC
   - Body material: MATRIX
   - Size: 12.25"

2. **Create Design Revision**
   - MAT number: MAT-12345-L4
   - Level: 4
   - Effective from: 2025-01-01

3. **Create Work Order**
   - Order type: NEW_BUILD
   - Design/MAT: Select revision
   - Customer info: Customer name, rig, well, field
   - Priority: NORMAL/HIGH/URGENT

4. **Create Job Card**
   - Link to work order
   - Department: MATRIX_INFILTRATION
   - Status: RELEASED

5. **Create Infiltration Batch**
   - Batch code: BATCH-2025-001
   - Furnace: FURNACE-1
   - Add job card to batch

6. **Track Progress**
   - Update batch status: LOADING → IN_FURNACE → COOLING → COMPLETED
   - Update job card route steps
   - Transfer to Finishing department

7. **Complete Manufacturing**
   - Finishing route steps
   - NDT & thread inspection
   - Final QC
   - Create Bit Instance with serial number

### Handling a Repair

1. **Create Work Order**
   - Order type: REPAIR
   - Bit instance: Select existing bit (e.g., 12345678)
   - Design/MAT: Current or updated design

2. **Create Evaluation Job Card**
   - Department: QC
   - Create EvaluationSummary
   - Damage assessment
   - Recommendation: REPAIR

3. **Create Repair Job Card**
   - Department: REPAIR
   - Route steps for repair process

4. **Update Bit Instance**
   - Increment repair index: 0 → 1
   - Update status: IN_REPAIR → IN_STOCK
   - Serial displays as "12345678-R1"

## QR Code Integration

### Generate QR Code
Visit: `/production/jobcards/<id>/qr/`
Returns PNG image with embedded URL

### Scan QR Code
QR contains URL: `/production/qr/<uuid>/`
Redirects to job card detail page

### Shop Floor Usage
1. Print job card with QR code
2. Operators scan with mobile device
3. Direct access to job details, route steps, and status updates

## Integration Notes

**Future Integration Points:**
- HR system: Operator management, departments, shifts
- Inventory: Cutters, powder mixes, consumables
- Logistics: Shipping, receiving, stock management
- ERP: Financial data, purchase orders, customer management

**Design for Integration:**
- Human-readable codes (wo_number, jobcard_code, batch_code)
- External reference fields
- Internal PKs separate from business codes
- RESTful URL structure

## Domain-Specific Notes

### Infiltration Process
Matrix bodies are produced using powder metallurgy:
1. Tungsten carbide powder mixed with binders
2. Powder loaded into molds with inserts (PDC cutters, nozzles)
3. Copper or bronze alloy positioned
4. Furnace cycle (controlled temperature, time)
5. Alloy infiltrates powder matrix
6. Cooling creates solid bit body
7. Demolding and post-processing

### Repair Economics
Bits are expensive assets:
- New PDC bit: $20,000 - $100,000+
- Repair cost: $5,000 - $30,000
- Multiple repairs extend bit life (R1, R2, R3...)
- Tracking repair history is critical

### Joint Venture (JV) Production
Some bits/bodies produced by partners:
- Semi-finished bodies received
- Completed in-house (machining, cutters, finishing)
- System tracks manufacturing source

## Contributing

When extending this system:
1. Follow Django best practices
2. Maintain comprehensive documentation
3. Add migrations for model changes
4. Update admin configurations
5. Extend templates for new functionality
6. Add appropriate indexes for queries

## License

Proprietary - Floor Management System C

---

**Version:** 1.0.0  
**Created:** 2025-11-23  
**Django Version:** 5.2.6  
**Python Version:** 3.11+
