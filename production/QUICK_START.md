# Production Department - Quick Start Guide

## Initial Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
# Enter username, email, and password when prompted
```

### 4. Load Sample Data (Optional but Recommended)
```bash
python manage.py create_sample_data
```

This creates:
- 3 Bit Designs (PDC Matrix, PDC Steel, Roller Cone)
- 3 Design Revisions with MAT numbers
- 2 Route Templates with full step sequences
- 5 Work Orders (3 new builds, 2 repairs)
- 3 Job Cards with QR codes
- 1 Infiltration Batch
- 1 Bit Instance

### 5. Start Development Server
```bash
python manage.py runserver
```

## Access the System

**Production Dashboard**: http://localhost:8000/production/  
**Admin Interface**: http://localhost:8000/admin/  
**Login Page**: http://localhost:8000/accounts/login/

## Quick Tour

### 1. Dashboard (Start Here)
Navigate to `/production/` to see:
- Statistics: Open orders, urgent WOs, active jobs, QC holds
- Recent work orders list
- Active jobs by department
- Infiltration batches in progress

### 2. Work Orders
**Create New Build**:
1. Click "Work Orders" → "Create New"
2. Fill in:
   - WO Number: WO-2025-0006
   - Order Type: New Build
   - Design/MAT: Select from dropdown
   - Customer: Your customer name
   - Priority: Normal/High/Urgent
3. Save

**Create Repair**:
1. Same as above, but select "Repair" as type
2. Select existing Bit Instance (if available)
3. System will track repair index (R1, R2, etc.)

### 3. Job Cards
**Create Job Card**:
1. Click "Job Cards" → "Create New"
2. Link to Work Order
3. Select Department:
   - Matrix/Infiltration (for matrix body production)
   - Finishing (for steel body or post-infiltration)
   - Repair (for repair work)
   - QC (for quality control)
4. Save and view QR code

**Scan QR Code**:
- Click "QR Code" button on job card detail page
- Print or display QR code
- Scan with mobile device to access job card

### 4. Bit Designs
**Create Design**:
1. Navigate to "Bit Management" → "Bit Designs"
2. Click "Create New"
3. Fill in:
   - Design Code: HD75WF
   - Type: PDC or Roller Cone
   - Body Material: Matrix or Steel (for PDC)
   - Size: 12.25 (in inches)
   - Blade Count: 7 (for PDC)
4. Save

**Create Revision**:
1. Go to admin interface `/admin/`
2. Navigate to "Bit design revisions"
3. Add new revision with MAT number

### 5. Infiltration Batches (Matrix Production)
**Create Batch**:
1. Navigate to "Infiltration"
2. Click "Create New"
3. Fill in:
   - Batch Code: BATCH-2025-002
   - Furnace: FURNACE-1 or FURNACE-2
   - Planned Start/End times
   - Temperature Profile (JSON or text)
   - Operator Name
   - Status: Planned → Loading → In Furnace → Cooling → Completed
4. Save

**Add Items to Batch**:
- Use admin interface to add InfiltrationBatchItem
- Link job cards to the batch
- Track individual mold IDs and powder mix codes

## Common Workflows

### Matrix-body PDC New Build

1. **Create Bit Design** (if new): HD75WF, PDC, Matrix, 12.25"
2. **Create Design Revision**: MAT-2025-001-L4
3. **Create Work Order**: 
   - Type: New Build
   - Select design revision
   - Customer: Schlumberger, Rig: RIG-1
4. **Create Job Card #1** (Infiltration):
   - Department: Matrix/Infiltration
   - Status: Released
5. **Create Infiltration Batch**:
   - Add job card to batch
   - Set status: In Furnace
6. **Update Batch Status**: Cooling → Completed
7. **Create Job Card #2** (Finishing):
   - Department: Finishing
   - Create route steps (machining, welding, brazing)
8. **Create QC Records**:
   - NDT Results (MPI, DPI, UT)
   - Thread Inspection
9. **Create Bit Instance**:
   - Serial: 20250002
   - Manufacturing Source: Internal Matrix
   - Link to work order
10. **Complete**: Update work order status to Completed

### Repair Workflow

1. **Create Work Order**:
   - Type: Repair
   - Select existing Bit Instance: 20250001
2. **Create Evaluation Job Card**:
   - Department: QC
   - Create EvaluationSummary:
     - Condition: Major Damage
     - Recommended Action: Repair
3. **Create Repair Job Card**:
   - Department: Repair
   - Route steps: Washing, damage mapping, body repair, hardfacing
4. **Create QC Records**: NDT, Thread Inspection
5. **Update Bit Instance**:
   - Increment repair_index: 0 → 1
   - Serial displays as "20250001-R1"
   - Status: In Stock
6. **Complete Work Order**

## Admin Interface Quick Access

Navigate to `/admin/` for:
- Bulk data entry
- Advanced filtering and search
- Inline editing (route steps, batch items)
- Data export (via list displays)
- Route template management

## Tips & Tricks

**Search Functionality**:
- All list views have search boxes
- Work Orders: Search by WO number, customer, rig
- Job Cards: Search by job card code, WO number
- Bit Designs: Search by design code, description

**Filters**:
- Use dropdown filters for:
  - Order Type (New Build, Repair, Evaluation)
  - Status (Draft, Open, In Progress, Completed)
  - Priority (Low, Normal, High, Urgent)
  - Department

**QR Codes**:
- Auto-generated for all job cards
- Access via: `/production/jobcards/<id>/qr/`
- Scan URL: `/production/qr/<code>/`
- Mobile-friendly access

**Pagination**:
- All lists paginated at 50 items
- Use page navigation at bottom of tables

## Troubleshooting

**Can't login?**
- Create superuser: `python manage.py createsuperuser`
- Default redirect: `/production/` (dashboard)

**No data showing?**
- Run: `python manage.py create_sample_data`
- Or create data via admin interface

**QR codes not showing?**
- Ensure `qrcode` and `Pillow` are installed
- Check URL is accessible

**Database errors?**
- Run migrations: `python manage.py migrate`
- Check PostgreSQL connection in settings

## Next Steps

1. **Customize Route Templates**:
   - Add/modify route steps for your processes
   - Set department assignments
   - Configure duration estimates

2. **Add Real Data**:
   - Import existing bit designs
   - Create your MAT numbers
   - Set up customer records

3. **Configure Users**:
   - Create operator accounts
   - Set department assignments
   - Configure permissions

4. **Integrate Systems**:
   - Connect to HR system for operators
   - Link to inventory for materials
   - Integrate with ERP for financials

## Support

For questions or issues:
1. Check the main README.md for detailed documentation
2. Review model definitions in `production/models.py`
3. Examine workflow examples in `production/README.md`

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-23
