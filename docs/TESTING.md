# Testing Documentation

This document describes the comprehensive testing suite for the Floor Management System.

## Overview

The system includes:
- **48+ unit tests** covering all major functionality
- **Sample data loading script** for development and demonstration
- **JSON fixtures** for quick data setup
- **Test coverage** for KSA compliance, quality control, and validation utilities

## Running Tests

### Run All Tests

```bash
python manage.py test
```

### Run Specific App Tests

```bash
# Inventory tests
python manage.py test inventory

# Purchasing tests
python manage.py test purchasing

# Core tests
python manage.py test core
```

### Run with Verbose Output

```bash
python manage.py test inventory -v 2
```

### Run Specific Test Cases

```bash
# Run only KSA utilities tests
python manage.py test inventory.tests.KSAUtilsTestCase

# Run a specific test method
python manage.py test inventory.tests.KSAUtilsTestCase.test_vat_number_validation_valid
```

## Test Coverage

### 1. KSA Utilities Tests (`KSAUtilsTestCase`)

Tests for Saudi Arabia compliance utilities:

- ✓ ZATCA QR code generation and decoding
- ✓ VAT number validation (valid and invalid cases)
- ✓ VAT number formatting
- ✓ HS code validation and formatting
- ✓ VAT calculations (15%)
- ✓ Zakat calculations (2.5%)
- ✓ Saudi postal code validation
- ✓ Saudi phone number validation (mobile and landline)
- ✓ Arabic numeral conversion
- ✓ Currency formatting in Arabic

**Example:**
```python
# Test VAT calculation
vat = ksa_utils.calculate_vat_amount(Decimal('1000.00'))
# Returns: Decimal('150.00')
```

### 2. KSA Compliance Models Tests

Tests for regulatory compliance models:

- ✓ `CompanyProfile` - Company legal information
- ✓ `ItemCertificate` - SABER, SASO certificate tracking
- ✓ `CustomsDeclaration` - FASAH customs clearance
- ✓ `CustomsDeclarationLine` - Duty and VAT calculation
- ✓ `Shipment` - Carrier tracking

**Example:**
```python
# Test certificate expiry checking
cert.is_expiring_soon  # True if expiring within 30 days
cert.days_until_expiry  # Number of days until expiry
```

### 3. Quality Control Tests

Tests for quality management:

- ✓ `QualityInspection` - PASS/FAIL/REJECT inspections
- ✓ `ItemBatch` - Expiry tracking and FEFO
- ✓ `UsedItemTracking` - Condition grading and maintenance

**Example:**
```python
# Test batch expiry
batch.is_expired()  # True if past expiry date
```

### 4. Validation Utilities Tests

Tests for error prevention:

- ✓ QR code validation (type checking, existence verification)
- ✓ Quantity validation (large numbers, decimal places)
- ✓ Stock availability checking
- ✓ Supervisor approval workflow
- ✓ Duplicate entry detection

**Example:**
```python
# Test QR code validation
qr_data = "ITEM:CUT-PDC-001|PDC Cutter|CUTTER"
item = StockOperationValidator.validate_qr_code(qr_data, expected_type='ITEM')
# Returns the Item object or raises ValidationError
```

## Sample Data

### Method 1: Management Command (Recommended)

Load comprehensive sample data using the management command:

```bash
# Load sample data
python manage.py load_sample_data

# Clear existing data and reload
python manage.py load_sample_data --clear
```

This creates:
- 4 test users (admin, operator, inspector, supervisor)
- 1 company profile (Saudi drilling bits manufacturer)
- 5 suppliers (USA, Germany, China, KSA, Italy)
- 6 item categories
- 6 units of measure
- 6+ items (PDC cutters, tungsten carbide, etc.)
- 2 warehouses with 7 locations
- Stock levels and transactions
- Item certificates (SABER, SASO)
- Customs declarations
- Shipments
- Quality inspections
- Item batches
- Used items tracking
- Purchase requests, orders, and receipts

**Test Login Credentials:**
```
Admin:      username=admin      password=admin123
Operator:   username=operator   password=password123
Inspector:  username=inspector  password=password123
Supervisor: username=supervisor password=password123
```

### Method 2: JSON Fixtures

Load basic data using Django fixtures:

```bash
python manage.py loaddata inventory/fixtures/sample_data.json
```

### Method 3: Manual Creation in Tests

Use Django's TestCase setUp methods to create test data:

```python
class MyTestCase(TestCase):
    def setUp(self):
        self.category = ItemCategory.objects.create(code='TEST', name='Test')
        self.uom = UnitOfMeasure.objects.create(code='EA', name='Each')
        self.item = Item.objects.create(
            item_code='TEST-001',
            name='Test Item',
            category=self.category,
            unit_of_measure=self.uom
        )
```

## Test Data Details

### Sample Items Created

| Item Code | Name | Type | HS Code | Origin |
|-----------|------|------|---------|--------|
| CUT-PDC-001 | PDC Cutter 13mm | CUTTER | 8207130000 | US |
| CUT-PDC-002 | PDC Cutter 16mm | CUTTER | 8207130000 | US |
| CUT-TCI-001 | Tungsten Carbide Insert | CUTTER | 8209001000 | DE |
| MAT-WC-001 | Tungsten Carbide Powder | MATRIX_POWDER | 2849901000 | CN |
| MAT-CO-001 | Cobalt Powder | MATRIX_POWDER | 8105201000 | CN |
| BIN-EPX-001 | Epoxy Resin | OTHER | 3907300000 | IT |

### Sample Locations

| Warehouse | Location Code | Name |
|-----------|--------------|------|
| WH-MAIN | RACK-A1 | Rack A - Level 1 |
| WH-MAIN | RACK-A2 | Rack A - Level 2 |
| WH-MAIN | SILO-01 | Powder Silo 1 |
| WH-QC | QC-INSPECT | QC Inspection Area |
| WH-QC | QC-QUARANTINE | Quarantine Zone |

### Sample Stock Levels

| Item | Location | Quantity |
|------|----------|----------|
| CUT-PDC-001 | RACK-A1 | 1,250 |
| CUT-PDC-002 | RACK-A1 | 950 |
| MAT-WC-001 | SILO-01 | 750 kg |

## Writing New Tests

### Test Structure

```python
from django.test import TestCase
from inventory.models import Item, ItemCategory, UnitOfMeasure

class MyModelTest(TestCase):
    """Test MyModel functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test objects
        self.category = ItemCategory.objects.create(code='TEST', name='Test')
    
    def test_model_creation(self):
        """Test that model can be created."""
        obj = MyModel.objects.create(name='Test')
        self.assertEqual(obj.name, 'Test')
    
    def test_model_str(self):
        """Test string representation."""
        obj = MyModel.objects.create(name='Test')
        self.assertEqual(str(obj), 'Expected String')
```

### Best Practices

1. **Use descriptive test names**: `test_vat_number_validation_valid` instead of `test_vat`
2. **Test one thing per test**: Each test method should test a single behavior
3. **Use setUp for common data**: Create shared test objects in setUp method
4. **Test edge cases**: Test invalid inputs, boundary conditions, and error cases
5. **Use assertions**: Use appropriate assertions (assertEqual, assertTrue, assertRaises)
6. **Add docstrings**: Document what each test is testing

### Example: Testing Validation

```python
def test_quantity_validation_too_large(self):
    """Test quantity validation with unreasonably large number."""
    with self.assertRaises(ValidationError) as context:
        StockOperationValidator.validate_quantity(15000, self.item)
    
    self.assertIn("unusually large", str(context.exception))
```

## Test Database

Django automatically creates a test database:
- Name: `test_floor_management_c` (based on your database name)
- Isolated from production/development data
- Destroyed after tests complete
- Migrations automatically applied

## Continuous Integration

For CI/CD pipelines:

```bash
# Run tests with coverage
coverage run --source='.' manage.py test
coverage report

# Generate HTML coverage report
coverage html
```

## Troubleshooting

### Database Connection Errors

If PostgreSQL is not running:
```bash
# Start PostgreSQL (example for Linux)
sudo service postgresql start

# For Docker
docker-compose up -d db
```

### Migration Errors

If migrations are missing:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Import Errors

If models can't be imported, ensure all apps are in INSTALLED_APPS:
```python
INSTALLED_APPS = [
    # ...
    'inventory',
    'purchasing',
    'core',
]
```

## Performance Testing

For load testing stock operations:

```bash
# Create multiple transactions
python manage.py shell
>>> from inventory.tests import create_bulk_transactions
>>> create_bulk_transactions(count=1000)
```

## Next Steps

1. Add integration tests for views
2. Add API endpoint tests
3. Add Selenium tests for UI
4. Set up coverage reporting
5. Add performance benchmarks

---

**Last Updated:** 2025-11-23
**Test Count:** 48+ tests
**Coverage:** Core models, utilities, and business logic
