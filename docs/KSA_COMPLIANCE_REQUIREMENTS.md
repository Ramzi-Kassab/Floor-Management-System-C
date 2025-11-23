# Saudi Arabia (KSA) Compliance & Regulatory Requirements

Complete guide for operating a logistics and manufacturing system in Saudi Arabia with full regulatory compliance.

## Table of Contents
1. [ZATCA Requirements (Tax Authority)](#zatca-requirements)
2. [Customs & Import/Export](#customs--importexport)
3. [Quality & Standards (SASO)](#quality--standards-saso)
4. [Statistical Reporting (GASTAT)](#statistical-reporting-gastat)
5. [Ministry of Commerce](#ministry-of-commerce)
6. [Shipping & Logistics](#shipping--logistics)
7. [Financial & Currency](#financial--currency)
8. [Language & Calendar](#language--calendar)

---

## ZATCA Requirements (Tax Authority)

### 1. VAT (Value Added Tax)
**Rate**: 15% (as of 2020)

**Requirements**:
- All taxable supplies must include VAT
- VAT Registration Number (TRN) must be displayed on all invoices
- Monthly/Quarterly VAT returns submission
- Track zero-rated, exempt, and out-of-scope supplies

**Implementation**:
```python
VAT_RATE = Decimal('0.15')  # 15%
VAT_TYPES = [
    ('STANDARD', 'Standard Rated - 15%'),
    ('ZERO_RATED', 'Zero Rated - 0%'),
    ('EXEMPT', 'Exempt'),
    ('OUT_OF_SCOPE', 'Out of Scope'),
]
```

### 2. E-Invoicing (Fatoora) - ZATCA Phase 1 & 2

**Phase 1 (Generation Phase)** - Mandatory from December 4, 2021:
- Generate electronic invoices (tax invoices and simplified tax invoices)
- Include mandatory fields as per ZATCA specifications
- Generate and display QR code on invoices
- Maintain invoice integrity (no alteration after issuance)

**Phase 2 (Integration Phase)** - Rolled out in waves:
- Integration with ZATCA platform
- Real-time invoice reporting
- Clearance/Reporting based on invoice type
- XML format (UBL 2.1 or equivalent)

**Mandatory Invoice Fields**:
1. Invoice serial number (unique sequential)
2. Invoice issue date (Gregorian and Hijri)
3. Supplier details:
   - Name
   - VAT registration number (15 digits)
   - Address
   - Commercial Registration (CR)
4. Customer details:
   - Name
   - VAT registration number (if B2B)
   - Address
5. Line items with:
   - Description
   - Quantity
   - Unit price
   - VAT rate
   - VAT amount
   - Total amount
6. Total amounts:
   - Subtotal (excluding VAT)
   - Total VAT
   - Total amount (including VAT)

**QR Code Specifications**:
- Must contain TLV (Tag-Length-Value) encoded data
- Fields encoded:
  1. Seller name (Tag 1)
  2. VAT registration number (Tag 2)
  3. Invoice timestamp (Tag 3)
  4. Invoice total (with VAT) (Tag 4)
  5. VAT amount (Tag 5)
- Base64 encoded
- Size: Minimum 3cm x 3cm when printed

**Sample QR Code Generation**:
```python
import base64
from struct import pack

def generate_fatoora_qr(seller_name, vat_number, timestamp, total_with_vat, vat_amount):
    """Generate ZATCA-compliant QR code data."""
    def tlv_encode(tag, value):
        value_bytes = value.encode('utf-8')
        length = len(value_bytes)
        return pack('B', tag) + pack('B', length) + value_bytes

    tlv_data = b''
    tlv_data += tlv_encode(1, seller_name)
    tlv_data += tlv_encode(2, vat_number)
    tlv_data += tlv_encode(3, timestamp)
    tlv_data += tlv_encode(4, f"{total_with_vat:.2f}")
    tlv_data += tlv_encode(5, f"{vat_amount:.2f}")

    return base64.b64encode(tlv_data).decode('utf-8')
```

### 3. Tax Registration Number (TRN)
- Format: 15 digits (e.g., 300012345600003)
- Must be validated before accepting supplier/customer records
- Display on all tax documents

**Validation**:
```python
def validate_saudi_vat_number(vat_number):
    """Validate Saudi VAT/TRN format."""
    if not vat_number:
        return False

    # Remove spaces and hyphens
    vat_clean = vat_number.replace(' ', '').replace('-', '')

    # Must be 15 digits
    if len(vat_clean) != 15:
        return False

    # Must be numeric
    if not vat_clean.isdigit():
        return False

    # First digit should be 3 (for standard)
    if not vat_clean.startswith('3'):
        return False

    # Last two digits are the check digits
    return True
```

---

## Customs & Import/Export

### 1. HS Codes (Harmonized System)
**Purpose**: Classify goods for customs duties and taxes

**Requirements**:
- All imported/exported items must have HS code
- Saudi Arabia uses 10-digit HS code (extension of international 6-digit)
- Determines applicable customs duties

**Implementation**:
```python
class Item:
    hs_code = models.CharField(
        max_length=10,
        blank=True,
        help_text="10-digit HS code for customs classification"
    )
    hs_code_description = models.TextField(blank=True)
    customs_duty_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Customs duty percentage"
    )
```

**Example HS Codes** (for drilling bits):
- `8207.13.00.00` - Rock drilling bits (with working part of sintered metal-carbides)
- `8207.19.00.00` - Other rock drilling or earth boring tools
- `8431.43.00.00` - Parts for boring or sinking machinery

### 2. Country of Origin
**Requirements**:
- Track country of origin for all items
- Certificate of Origin (CoO) required for imports
- Preferential tariffs based on origin (GCC, trade agreements)

**Implementation**:
```python
COUNTRY_CHOICES = [
    ('SA', 'Saudi Arabia'),
    ('AE', 'United Arab Emirates'),
    ('CN', 'China'),
    ('US', 'United States'),
    ('DE', 'Germany'),
    # ... all countries
]

class Item:
    country_of_origin = models.CharField(
        max_length=2,
        choices=COUNTRY_CHOICES,
        blank=True,
        help_text="ISO 3166-1 alpha-2 country code"
    )
    certificate_of_origin_required = models.BooleanField(default=False)
```

### 3. SABER (Saudi Product Safety Program)
**Purpose**: Ensure imported products meet Saudi standards

**Requirements**:
- SABER certificate (PCOC - Product Certificate of Conformity) for regulated products
- SABER certificate number must be provided for customs clearance
- Track certificate validity dates

**Implementation**:
```python
class ItemCertificate(models.Model):
    """Track regulatory certificates for items."""

    CERTIFICATE_TYPES = [
        ('SABER', 'SABER Certificate'),
        ('SFDA', 'SFDA Certificate'),
        ('SASO', 'SASO Certificate'),
        ('COO', 'Certificate of Origin'),
        ('COC', 'Certificate of Conformity'),
        ('HALAL', 'Halal Certificate'),
    ]

    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='certificates')
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    certificate_number = models.CharField(max_length=100)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=200)
    certificate_url = models.URLField(blank=True, help_text="Link to certificate document")
    is_valid = models.BooleanField(default=True)

    def check_validity(self):
        """Check if certificate is still valid."""
        from datetime import date
        if self.expiry_date < date.today():
            self.is_valid = False
            self.save()
        return self.is_valid
```

### 4. FASAH (Customs Clearance System)
**Purpose**: Electronic customs clearance

**Requirements**:
- Customs declaration number
- Import/Export license numbers
- Shipper and consignee details
- Bill of Lading / Airway Bill numbers

**Implementation**:
```python
class CustomsDeclaration(models.Model):
    """Track customs declarations for imports/exports."""

    DECLARATION_TYPE_CHOICES = [
        ('IMPORT', 'Import Declaration'),
        ('EXPORT', 'Export Declaration'),
        ('RE_EXPORT', 'Re-Export Declaration'),
    ]

    declaration_number = models.CharField(max_length=50, unique=True)
    declaration_type = models.CharField(max_length=20, choices=DECLARATION_TYPE_CHOICES)
    declaration_date = models.DateField()

    # Reference to purchase order or goods receipt
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.PROTECT, null=True, blank=True)
    goods_receipt = models.ForeignKey('GoodsReceipt', on_delete=models.PROTECT, null=True, blank=True)

    # Shipping details
    bill_of_lading = models.CharField(max_length=100, blank=True)
    airway_bill = models.CharField(max_length=100, blank=True)
    port_of_entry = models.CharField(max_length=100, help_text="e.g., Jeddah Islamic Port")

    # Customs broker
    customs_broker_name = models.CharField(max_length=200, blank=True)
    customs_broker_license = models.CharField(max_length=100, blank=True)

    # Financial
    total_customs_value = models.DecimalField(max_digits=15, decimal_places=2)
    total_customs_duty = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_vat = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    # Status
    clearance_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Clearance'),
            ('UNDER_REVIEW', 'Under Review'),
            ('CLEARED', 'Cleared'),
            ('HELD', 'Held by Customs'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )
    clearance_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## Quality & Standards (SASO)

### Saudi Standards, Metrology and Quality Organization

**Requirements**:
- Quality certificates for manufactured products
- Standards compliance documentation
- Calibration certificates for measuring equipment

**Key Standards**:
- SASO 2902:2018 - Quality Management Systems
- SASO ISO 9001 - Quality management
- Product-specific standards for drilling equipment

---

## Statistical Reporting (GASTAT)

### General Authority for Statistics

**Requirements**:
- Monthly production statistics
- Import/Export quantities and values
- Inventory levels
- Employment statistics

**Implementation**:
```python
class MonthlyStatisticsReport(models.Model):
    """Monthly statistics for GASTAT reporting."""

    report_month = models.DateField(help_text="First day of reporting month")

    # Production statistics
    total_production_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    total_production_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Import statistics
    total_imports_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    total_imports_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Export statistics
    total_exports_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    total_exports_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Inventory
    ending_inventory_value = models.DecimalField(max_digits=15, decimal_places=2)

    submitted_date = models.DateTimeField(null=True, blank=True)
    submitted_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
```

---

## Ministry of Commerce

### Commercial Registration (CR)

**Requirements**:
- Commercial Registration number for the company
- Display on all official documents
- Renewal tracking

**Implementation**:
```python
class CompanyProfile(models.Model):
    """Company legal and compliance information."""

    # Legal
    company_name_arabic = models.CharField(max_length=200)
    company_name_english = models.CharField(max_length=200)
    commercial_registration = models.CharField(max_length=20, unique=True, help_text="CR Number")
    cr_expiry_date = models.DateField()

    # Tax
    vat_registration_number = models.CharField(max_length=15, help_text="15-digit TRN")
    vat_registration_date = models.DateField()

    # Industrial
    industrial_license_number = models.CharField(max_length=50, blank=True)
    industrial_license_expiry = models.DateField(null=True, blank=True)

    # Zakat
    zakat_certificate_number = models.CharField(max_length=50, blank=True)
    zakat_certificate_expiry = models.DateField(null=True, blank=True)

    # Address
    address_arabic = models.TextField()
    address_english = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
```

---

## Shipping & Logistics

### Local Shipping Companies

**Major Carriers in KSA**:
- SMSA Express
- Aramex
- DHL Saudi Arabia
- FedEx
- Saudi Post (SPL)
- UPS Saudi Arabia

**Implementation**:
```python
class Shipment(models.Model):
    """Track shipments and deliveries."""

    CARRIER_CHOICES = [
        ('SMSA', 'SMSA Express'),
        ('ARAMEX', 'Aramex'),
        ('DHL', 'DHL Saudi Arabia'),
        ('FEDEX', 'FedEx'),
        ('SPL', 'Saudi Post'),
        ('UPS', 'UPS'),
        ('OTHER', 'Other'),
    ]

    shipment_number = models.CharField(max_length=50, unique=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES)
    waybill_number = models.CharField(max_length=100, help_text="Tracking number from carrier")

    # References
    sales_order = models.ForeignKey('SalesOrder', on_delete=models.PROTECT, null=True, blank=True)
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.PROTECT, null=True, blank=True)

    # Addresses
    origin_address = models.TextField()
    destination_address = models.TextField()

    # Dates
    pickup_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Pickup'),
            ('PICKED_UP', 'Picked Up'),
            ('IN_TRANSIT', 'In Transit'),
            ('OUT_FOR_DELIVERY', 'Out for Delivery'),
            ('DELIVERED', 'Delivered'),
            ('RETURNED', 'Returned'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='PENDING'
    )

    # Costs
    freight_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    tracking_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
```

---

## Financial & Currency

### Saudi Riyal (SAR)

**Requirements**:
- All financial transactions in SAR
- Exchange rate tracking for foreign currency purchases
- Rounding rules (2 decimal places, 5 halalas = 0.05 SAR)

**Implementation**:
```python
# settings.py
CURRENCY = 'SAR'
CURRENCY_SYMBOL = 'ر.س'  # Arabic
CURRENCY_SYMBOL_EN = 'SAR'  # English

# Zakat calculation (2.5% on certain assets)
ZAKAT_RATE = Decimal('0.025')

def calculate_zakat(zakatable_assets):
    """Calculate Zakat on zakatable assets."""
    return zakatable_assets * ZAKAT_RATE
```

---

## Language & Calendar

### 1. Arabic Language Support

**Requirements**:
- All official documents in Arabic (or bilingual)
- Right-to-Left (RTL) text support
- Arabic number formats

**Implementation**:
```python
# settings.py
LANGUAGES = [
    ('ar', 'العربية'),
    ('en', 'English'),
]

LANGUAGE_CODE = 'ar'  # Default Arabic

# Template usage
{% load i18n %}
<html dir="{% if LANGUAGE_CODE == 'ar' %}rtl{% else %}ltr{% endif %}">
```

### 2. Hijri Calendar

**Requirements**:
- Display Hijri date alongside Gregorian
- Some official documents require Hijri date

**Implementation**:
```python
from hijri_converter import Gregorian, Hijri

def get_hijri_date(gregorian_date):
    """Convert Gregorian date to Hijri."""
    g = Gregorian(
        gregorian_date.year,
        gregorian_date.month,
        gregorian_date.day
    )
    h = g.to_hijri()
    return f"{h.day:02d}/{h.month:02d}/{h.year}"

# Example usage:
invoice_date_gregorian = date(2025, 11, 23)
invoice_date_hijri = get_hijri_date(invoice_date_gregorian)
# Returns: "21/05/1447" (21 Jumada al-Ula 1447)
```

---

## Summary Checklist

### Must-Have Features:
- [x] VAT (15%) calculation and tracking
- [x] E-Invoicing QR code generation (Fatoora)
- [ ] TRN validation
- [ ] HS Code tracking
- [ ] Country of Origin tracking
- [ ] SABER certificate management
- [ ] Customs declaration tracking
- [ ] Arabic language support (RTL)
- [ ] Hijri calendar alongside Gregorian
- [ ] SAR currency handling

### Nice-to-Have Features:
- [ ] Direct ZATCA API integration (Phase 2)
- [ ] FASAH customs integration
- [ ] GASTAT automated reporting
- [ ] Zakat calculation
- [ ] Shipping carrier integration (SMSA, Aramex, etc.)

---

## External Resources

- **ZATCA Portal**: https://zatca.gov.sa/
- **E-Invoicing SDK**: https://zatca.gov.sa/en/E-Invoicing/
- **SABER Portal**: https://saber.sa/
- **Saudi Customs**: https://www.customs.gov.sa/
- **SASO**: https://www.saso.gov.sa/
- **GASTAT**: https://www.stats.gov.sa/
