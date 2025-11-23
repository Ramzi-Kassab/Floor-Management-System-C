# Logistics Module Documentation

## Overview

The Logistics module is a comprehensive inventory and purchasing management system designed for a drilling bits manufacturing facility. It manages everything from raw materials (PDC cutters, matrix powders, steel bodies) to finished goods, JV semi-finished bodies, and consumables.

## Architecture

### Apps Structure

The module consists of two Django apps:

1. **inventory** - Manages items, warehouses, stock levels, and transactions
2. **purchasing** - Manages the procurement process (PR → PO → GRN)

### Database Models

#### Inventory App (10 Models)

**Master Data:**
- `Supplier` - Supplier information and contact details
- `ItemCategory` - Hierarchical item categorization
- `UnitOfMeasure` - Units (EA, KG, L, M, etc.)
- `Item` - Item master data with 14 item types

**Warehouse Management:**
- `Warehouse` - Physical warehouse locations
- `Location` - Storage locations within warehouses (with QR code support)

**Stock Classification:**
- `ConditionType` - NEW, USED, REPAIRABLE, SCRAP, REWORK
- `OwnershipType` - OWN, CUSTOMER, CONSIGNMENT, JV_OWNED, RENTAL

**Stock Tracking:**
- `StockLevel` - Current stock quantities (unique per item + location + condition + ownership)
- `StockTransaction` - Complete audit trail of all stock movements

#### Purchasing App (6 Models)

**Purchase Request Flow:**
- `PurchaseRequest` - PR header (Draft → Submitted → Approved → Ordered → Closed)
- `PurchaseRequestLine` - PR line items

**Purchase Order Flow:**
- `PurchaseOrder` - PO header with supplier and payment terms
- `PurchaseOrderLine` - PO line items with pricing

**Goods Receipt Flow:**
- `GoodsReceipt` - GRN header
- `GoodsReceiptLine` - GRN line items (automatically updates stock)

## Key Features

### 1. Automatic Stock Management

When a `GoodsReceiptLine` is saved, the system automatically:
1. Creates a `StockTransaction` with type `PURCHASE_RECEIPT`
2. Updates or creates the corresponding `StockLevel`
3. Maintains full audit trail

```python
# Example: Receiving goods automatically updates stock
grn_line = GoodsReceiptLine.objects.create(
    goods_receipt=grn,
    purchase_order_line=po_line,
    received_quantity=100,
    location=location,
    condition_type=new_condition,
    ownership_type=own
)
# Stock is automatically updated!
```

### 2. Stock Adjustment

Create stock adjustments for:
- Initial stock entry
- Stock corrections
- Cycle count adjustments

**URL:** `/inventory/stock/adjustment/`

```python
# Positive quantity adds stock
# Negative quantity removes stock
```

### 3. Stock Transfer

Transfer stock between locations with validation:
- Checks if sufficient stock exists at source location
- Creates transaction record
- Updates stock levels at both locations

**URL:** `/inventory/stock/transfer/`

### 4. Low Stock Alerts

View items below reorder level with urgency classification:
- **Critical** - Stock < 25% of reorder level (red badge)
- **Warning** - Stock 25-50% of reorder level (yellow badge)
- **Low** - Stock 50-100% of reorder level (blue badge)

**URL:** `/inventory/stock/low-stock/`

### 5. QR Code Generation

Generate printable QR codes for:
- **Items:** `ITEM:{item_code}|{name}|{category}`
- **Locations:** `LOC:{warehouse_code}|{location_code}|{name}`

**URLs:**
- Items: `/inventory/items/<id>/qrcode/`
- Locations: `/inventory/locations/<id>/qrcode/`

### 6. Multi-dimensional Stock Tracking

Stock is tracked by:
- Item
- Location
- Condition (NEW, USED, REPAIRABLE, SCRAP, REWORK)
- Ownership (OWN, CUSTOMER, CONSIGNMENT, JV_OWNED, RENTAL)

This allows precise tracking of:
- Own new cutters vs. customer-owned used cutters
- JV-owned semi-finished bodies
- Consignment stock from suppliers

## Setup & Installation

### 1. Install Dependencies

Dependencies are already in `requirements.txt`:
- Django 5.2.6
- qrcode 8.0 (for QR code generation)

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Initialize Master Data

```bash
# Load ConditionTypes, OwnershipTypes, UOMs, and Categories
python manage.py init_logistics_data

# Create sample warehouse with locations
python manage.py create_sample_warehouse
```

### 4. Create Superuser

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

## Usage Guide

### Initial Setup Workflow

1. **Load Master Data**
   ```bash
   python manage.py init_logistics_data
   python manage.py create_sample_warehouse
   ```

2. **Add Suppliers** (via admin or UI)
   - Navigate to `/inventory/suppliers/create/`
   - Add supplier code, name, contact details

3. **Create Items** (via admin or UI)
   - Navigate to `/inventory/items/create/`
   - Assign category, UOM, item type
   - Set reorder level and preferred supplier

4. **Initial Stock Entry**
   - Navigate to `/inventory/stock/adjustment/`
   - Add initial stock with condition and ownership

### Purchase-to-Receipt Workflow

1. **Create Purchase Request**
   - Navigate to `/purchasing/pr/create/`
   - Add items and quantities needed
   - Submit for approval

2. **Create Purchase Order**
   - Navigate to `/purchasing/po/create/`
   - Select supplier
   - Add line items with pricing
   - Send to supplier

3. **Create Goods Receipt**
   - Navigate to `/purchasing/grn/create/`
   - Select PO
   - Add received items with location, condition, and ownership
   - **Stock is automatically updated!**

### Stock Operations

**Adjust Stock:**
```
/inventory/stock/adjustment/
```
Use for corrections or initial stock entry

**Transfer Stock:**
```
/inventory/stock/transfer/
```
Move stock between warehouse locations

**View Low Stock:**
```
/inventory/stock/low-stock/
```
See items needing reorder

**View Transactions:**
```
/inventory/transactions/
```
Full audit trail of all stock movements

## URL Structure

### Inventory URLs (`/inventory/`)

**Dashboard:**
- `/` - Inventory dashboard

**Master Data:**
- `/items/` - List items
- `/items/create/` - Create item
- `/items/<id>/` - View item details
- `/items/<id>/edit/` - Edit item
- `/items/<id>/qrcode/` - Generate QR code

- `/suppliers/` - List suppliers
- `/categories/` - List categories
- `/warehouses/` - List warehouses
- `/locations/` - List locations

**Stock Management:**
- `/stock/` - Stock overview
- `/stock/adjustment/` - Create adjustment
- `/stock/transfer/` - Transfer stock
- `/stock/low-stock/` - Low stock items
- `/transactions/` - Transaction history

### Purchasing URLs (`/purchasing/`)

**Dashboard:**
- `/` - Purchasing dashboard

**Purchase Requests:**
- `/pr/` - List PRs
- `/pr/create/` - Create PR
- `/pr/<id>/` - View PR details

**Purchase Orders:**
- `/po/` - List POs
- `/po/create/` - Create PO
- `/po/<id>/` - View PO details

**Goods Receipts:**
- `/grn/` - List GRNs
- `/grn/create/` - Create GRN
- `/grn/<id>/` - View GRN details

## Admin Interface

Comprehensive Django admin interface with:
- Inline editing for line items
- Search and filtering on all models
- Date hierarchy for transactions
- Raw ID fields for performance

Access: `/admin/`

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test inventory purchasing

# Run specific test class
python manage.py test inventory.tests.StockLevelTest

# Run with verbosity
python manage.py test --verbosity=2
```

Test coverage includes:
- Model creation and constraints
- String representations
- Relationships
- Unique constraints
- Transaction types

## Future Enhancements

### Planned Features
- Mobile app for QR code scanning
- Barcode label printing
- Excel/CSV import/export
- Advanced reporting and analytics
- Integration with external ERP systems
- Email notifications for low stock
- Automatic PR generation based on reorder levels

### Integration Points

The module is designed for loose coupling with future modules:

**Production Module:**
- Issue materials to production via `StockTransaction` with type `ISSUE_TO_PRODUCTION`
- Return materials via `RETURN_FROM_PRODUCTION`

**External ERP:**
- All major models have `external_reference` field
- Stable codes: `item_code`, `pr_number`, `po_number`, `grn_number`

## Best Practices

### Item Codes
Use meaningful prefixes:
- `CUTTER-PDC-19MM` - PDC Cutter 19mm
- `MATRIX-WC-100KG` - Tungsten Carbide Matrix 100kg bag
- `STEEL-BODY-8.5` - Steel body for 8.5" bit

### Location Codes
Use hierarchical naming:
- `CUTTER-RACK-01` - Cutter storage rack 1
- `POWDER-SILO-1` - Powder silo 1
- `JV-AREA-A1` - JV body storage area A1

### Transaction References
Use consistent reference formats:
- `ADJ-2025-001` - Adjustments
- `TRF-2025-001` - Transfers
- `PO-2025-001` - Purchase orders
- `GRN-2025-001` - Goods receipts

## Troubleshooting

### Common Issues

**1. Cannot create stock adjustment**
- Ensure ConditionTypes and OwnershipTypes are loaded
- Run: `python manage.py init_logistics_data`

**2. Stock transfer fails with "Insufficient stock"**
- Check the exact combination of item + location + condition + ownership
- View stock levels at: `/inventory/stock/`

**3. QR codes not displaying**
- Ensure `qrcode` package is installed
- Check `requirements.txt`

**4. GRN not updating stock**
- This is automatic - check StockTransaction and StockLevel tables
- View transactions at: `/inventory/transactions/`

## Support

For issues or questions:
- Check Django logs for errors
- Review transaction history for audit trail
- Use admin interface for detailed model inspection

## License

Part of the Floor Management System C project.
