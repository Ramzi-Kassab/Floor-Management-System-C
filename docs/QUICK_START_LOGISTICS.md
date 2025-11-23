# Logistics Module - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

### Step 2: Run Migrations

```bash
python manage.py migrate
```

### Step 3: Initialize Master Data

```bash
# Load essential master data (ConditionTypes, OwnershipTypes, UOMs, Categories)
python manage.py init_logistics_data

# Create sample warehouse with locations
python manage.py create_sample_warehouse
```

You should see:
```
✓ Condition Types loaded successfully
✓ Ownership Types loaded successfully
✓ Units of Measure loaded successfully
✓ Item Categories loaded successfully
✓ Created warehouse: WH-MAIN
✓ Created 11 locations
```

### Step 4: Create Admin User

```bash
python manage.py createsuperuser
```

### Step 5: Run the Server

```bash
python manage.py runserver
```

## 📍 Access the System

### Web Interface
- **Inventory Dashboard:** http://localhost:8000/inventory/
- **Purchasing Dashboard:** http://localhost:8000/purchasing/
- **Admin Interface:** http://localhost:8000/admin/

### First Login
1. Go to http://localhost:8000/admin/
2. Login with your superuser credentials
3. Navigate to Inventory or Purchasing from the top menu

## 🎯 Common First Tasks

### Add Your First Item

1. Navigate to: **Inventory → Items → Add Item**
   - Or go to: http://localhost:8000/inventory/items/create/

2. Fill in:
   - **Item Code:** CUTTER-PDC-19MM
   - **Name:** PDC Cutter 19mm
   - **Category:** Cutters
   - **Unit of Measure:** EA (Each)
   - **Type:** PDC Cutter
   - **Reorder Level:** 100

3. Click **Save**

### Add Initial Stock

1. Navigate to: **Inventory → Stock Adjustment**
   - Or go to: http://localhost:8000/inventory/stock/adjustment/

2. Fill in:
   - **Item:** Select your item
   - **Location:** CUTTER-RACK-01
   - **Condition:** NEW
   - **Ownership:** OWN
   - **Quantity:** 500
   - **Reference:** INITIAL-STOCK
   - **Notes:** Initial stock entry

3. Click **Create Adjustment**

Your stock is now in the system! View it at: http://localhost:8000/inventory/stock/

### Create a Supplier

1. Navigate to: **Inventory → Suppliers → Add Supplier**
2. Fill in supplier details
3. Save

### Generate QR Code

1. Go to any item detail page
2. Click **QR Code** button
3. Print the QR code for labeling

## 📊 What's Included?

### Master Data (Pre-loaded)

**Condition Types:**
- NEW
- USED
- REPAIRABLE
- SCRAP
- REWORK

**Ownership Types:**
- OWN (Company owned)
- CUSTOMER (Customer owned, held for them)
- CONSIGNMENT (Supplier consignment)
- JV_OWNED (Joint venture partner)
- RENTAL (Rented/leased)

**Units of Measure:**
- EA (Each)
- KG (Kilogram)
- L (Liter)
- M (Meter)
- G (Gram)
- TON (Metric Ton)
- SET, BOX, PACK

**Item Categories:**
- Cutters
- Matrix Materials
- Steel Components
- JV Bodies
- Upper Sections
- Hardfacing Materials
- Consumables
- Tools
- Spare Parts
- Gases

**Sample Warehouse (WH-MAIN):**
- CUTTER-RACK-01, CUTTER-RACK-02
- POWDER-SILO-1, POWDER-SILO-2
- STEEL-AREA-A
- JV-BODY-AREA
- UPPER-RACK
- CONSUMABLE-01
- TOOL-ROOM
- ADJUSTMENT (virtual)
- SCRAP (virtual)

## 🔄 Complete Workflow Example

### Purchase-to-Stock Workflow

**1. Create Purchase Request**
```
Purchasing → PRs → Create PR
- Add items you need
- Set required dates
- Submit
```

**2. Create Purchase Order**
```
Purchasing → POs → Create PO
- Select supplier
- Add items with prices
- Save and send to supplier
```

**3. Receive Goods**
```
Purchasing → GRNs → Create GRN
- Select the PO
- Add received quantities
- Select storage location
- Set condition (usually NEW)
- Set ownership (usually OWN)
- Save
```

**Stock is automatically updated!** ✨

Check: http://localhost:8000/inventory/stock/

## 🛠️ Useful Commands

```bash
# View all management commands
python manage.py help

# Initialize logistics data
python manage.py init_logistics_data

# Create sample warehouse
python manage.py create_sample_warehouse

# Check for issues
python manage.py check

# Run tests
python manage.py test inventory purchasing
```

## 📱 Mobile Usage (Future)

QR codes are ready for mobile scanning apps. The format is:
- Items: `ITEM:{code}|{name}|{category}`
- Locations: `LOC:{warehouse}|{location}|{name}`

## 🆘 Quick Troubleshooting

**Problem:** Can't see ConditionTypes or OwnershipTypes in dropdowns
**Solution:** Run `python manage.py init_logistics_data`

**Problem:** Stock adjustment not working
**Solution:** Ensure all fixtures are loaded. Check admin for ConditionType and OwnershipType records.

**Problem:** QR codes not showing
**Solution:** Ensure `qrcode` package is installed: `pip install qrcode==8.0`

## 📚 Learn More

- Full documentation: `docs/LOGISTICS_MODULE.md`
- Model details: Check `inventory/models.py` and `purchasing/models.py`
- Admin interface: http://localhost:8000/admin/

## ✅ Checklist

- [ ] Dependencies installed
- [ ] Migrations run
- [ ] Master data initialized
- [ ] Sample warehouse created
- [ ] Superuser created
- [ ] Server running
- [ ] First item added
- [ ] Initial stock entered
- [ ] Supplier added

You're ready to go! 🎉
