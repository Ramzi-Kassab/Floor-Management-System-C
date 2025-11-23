"""
KSA (Saudi Arabia) Compliance Models
Handles regulatory requirements for operating in Saudi Arabia including:
- ZATCA (Tax Authority) compliance
- Customs and import/export
- Certificates and standards
- Company profile and legal requirements
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, RegexValidator
from decimal import Decimal
from datetime import date


# ==================== VAT Configuration ====================

VAT_RATE = Decimal('0.15')  # 15% VAT in Saudi Arabia

VAT_TYPE_CHOICES = [
    ('STANDARD', 'Standard Rated - 15%'),
    ('ZERO_RATED', 'Zero Rated - 0%'),
    ('EXEMPT', 'Exempt'),
    ('OUT_OF_SCOPE', 'Out of Scope'),
]


# ==================== Company Profile ====================

class CompanyProfile(models.Model):
    """
    Company legal and compliance information for KSA operations.
    Singleton model - only one instance should exist.
    """

    # Legal Information
    company_name_arabic = models.CharField(max_length=200, help_text="Company name in Arabic")
    company_name_english = models.CharField(max_length=200, help_text="Company name in English")

    commercial_registration = models.CharField(
        max_length=20,
        unique=True,
        help_text="Commercial Registration (CR) Number"
    )
    cr_issue_date = models.DateField(help_text="CR issue date")
    cr_expiry_date = models.DateField(help_text="CR expiry date")

    # Tax Information
    vat_registration_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^3\d{14}$',
                message='VAT number must be 15 digits starting with 3'
            )
        ],
        help_text="15-digit Tax Registration Number (TRN)"
    )
    vat_registration_date = models.DateField()

    # Industrial License
    industrial_license_number = models.CharField(max_length=50, blank=True)
    industrial_license_issue_date = models.DateField(null=True, blank=True)
    industrial_license_expiry = models.DateField(null=True, blank=True)

    # Zakat
    zakat_certificate_number = models.CharField(max_length=50, blank=True)
    zakat_certificate_expiry = models.DateField(null=True, blank=True)

    # Address
    address_arabic = models.TextField(help_text="Full address in Arabic")
    address_english = models.TextField(help_text="Full address in English")
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    building_number = models.CharField(max_length=10, blank=True)
    additional_number = models.CharField(max_length=10, blank=True)

    # Contact
    phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    website = models.URLField(blank=True)

    # E-Invoicing Settings
    einvoice_enabled = models.BooleanField(default=True, help_text="Enable ZATCA E-Invoicing")
    einvoice_environment = models.CharField(
        max_length=20,
        choices=[
            ('SANDBOX', 'Sandbox/Testing'),
            ('PRODUCTION', 'Production'),
        ],
        default='SANDBOX'
    )

    # Logo for invoices
    logo_url = models.URLField(blank=True, help_text="Company logo URL for documents")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Company Profile (KSA)'
        verbose_name_plural = 'Company Profile (KSA)'

    def __str__(self):
        return f"{self.company_name_english} (CR: {self.commercial_registration})"

    def save(self, *args, **kwargs):
        """Ensure only one company profile exists."""
        if not self.pk and CompanyProfile.objects.exists():
            raise ValueError('Only one Company Profile can exist')
        return super().save(*args, **kwargs)

    @property
    def is_cr_valid(self):
        """Check if CR is still valid."""
        return self.cr_expiry_date >= date.today()

    @property
    def is_industrial_license_valid(self):
        """Check if industrial license is still valid."""
        if self.industrial_license_expiry:
            return self.industrial_license_expiry >= date.today()
        return False


# ==================== Item Certificates ====================

class ItemCertificate(models.Model):
    """
    Track regulatory certificates for items.
    Includes SABER, SFDA, SASO, and other certifications.
    """

    CERTIFICATE_TYPES = [
        ('SABER', 'SABER Certificate (Product Conformity)'),
        ('SFDA', 'SFDA Certificate (Food & Drug Authority)'),
        ('SASO', 'SASO Certificate (Saudi Standards)'),
        ('COO', 'Certificate of Origin'),
        ('COC', 'Certificate of Conformity'),
        ('HALAL', 'Halal Certificate'),
        ('ISO', 'ISO Certification'),
        ('CALIBRATION', 'Calibration Certificate'),
        ('OTHER', 'Other Certificate'),
    ]

    item = models.ForeignKey(
        'Item',
        on_delete=models.CASCADE,
        related_name='ksa_certificates'
    )

    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES)
    certificate_number = models.CharField(max_length=100)
    certificate_name = models.CharField(max_length=200, help_text="Certificate name/title")

    issue_date = models.DateField()
    expiry_date = models.DateField(help_text="Leave blank if certificate doesn't expire")

    issuing_authority = models.CharField(max_length=200, help_text="Organization that issued certificate")
    issuing_country = models.CharField(max_length=2, default='SA', help_text="ISO country code")

    certificate_url = models.URLField(blank=True, help_text="Link to certificate document/PDF")
    is_valid = models.BooleanField(default=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Item Certificate (KSA)'
        verbose_name_plural = 'Item Certificates (KSA)'

    def __str__(self):
        return f"{self.get_certificate_type_display()} - {self.certificate_number} ({self.item.item_code})"

    def check_validity(self):
        """Check if certificate is still valid based on expiry date."""
        if self.expiry_date and self.expiry_date < date.today():
            self.is_valid = False
            self.save()
            return False
        return True

    @property
    def days_until_expiry(self):
        """Calculate days until certificate expires."""
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None

    @property
    def is_expiring_soon(self):
        """Check if certificate expires in next 30 days."""
        days = self.days_until_expiry
        return days is not None and 0 <= days <= 30


# ==================== Customs Declarations ====================

class CustomsDeclaration(models.Model):
    """
    Track customs declarations for imports and exports.
    Integrates with FASAH (Saudi Customs System).
    """

    DECLARATION_TYPE_CHOICES = [
        ('IMPORT', 'Import Declaration'),
        ('EXPORT', 'Export Declaration'),
        ('RE_EXPORT', 'Re-Export Declaration'),
        ('TEMPORARY', 'Temporary Import'),
    ]

    declaration_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="FASAH declaration number"
    )
    declaration_type = models.CharField(max_length=20, choices=DECLARATION_TYPE_CHOICES)
    declaration_date = models.DateField()

    # References
    purchase_order = models.ForeignKey(
        'purchasing.PurchaseOrder',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='customs_declarations'
    )
    goods_receipt = models.ForeignKey(
        'purchasing.GoodsReceipt',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='customs_declarations'
    )

    # Shipping details
    bill_of_lading = models.CharField(max_length=100, blank=True, help_text="B/L number")
    airway_bill = models.CharField(max_length=100, blank=True, help_text="AWB number")
    container_number = models.CharField(max_length=50, blank=True)

    port_of_entry = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Jeddah Islamic Port, King Abdulaziz Port"
    )
    port_of_exit = models.CharField(max_length=100, blank=True)

    # Parties
    importer_exporter = models.CharField(max_length=200, help_text="Company name")
    importer_exporter_cr = models.CharField(max_length=20, help_text="CR number")

    supplier_name = models.CharField(max_length=200, blank=True)
    supplier_country = models.CharField(max_length=2, blank=True, help_text="ISO country code")

    # Customs broker
    customs_broker_name = models.CharField(max_length=200, blank=True)
    customs_broker_license = models.CharField(max_length=100, blank=True)

    # Financial
    total_customs_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text="Total value for customs purposes (CIF)"
    )
    total_customs_duty = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total customs duty amount"
    )
    total_vat = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Total VAT on import"
    )
    other_fees = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Other fees (storage, inspection, etc.)"
    )

    # Status
    clearance_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Submission'),
            ('SUBMITTED', 'Submitted to Customs'),
            ('UNDER_REVIEW', 'Under Review'),
            ('INSPECTION_REQUIRED', 'Inspection Required'),
            ('CLEARED', 'Cleared'),
            ('HELD', 'Held by Customs'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )
    submission_date = models.DateField(null=True, blank=True)
    clearance_date = models.DateField(null=True, blank=True)

    # Documents
    commercial_invoice_url = models.URLField(blank=True)
    packing_list_url = models.URLField(blank=True)
    certificate_of_origin_url = models.URLField(blank=True)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-declaration_date', '-declaration_number']
        verbose_name = 'Customs Declaration'
        verbose_name_plural = 'Customs Declarations'

    def __str__(self):
        return f"{self.declaration_number} - {self.get_declaration_type_display()} ({self.declaration_date})"

    @property
    def total_amount_payable(self):
        """Calculate total amount payable to customs."""
        return self.total_customs_duty + self.total_vat + self.other_fees

    @property
    def is_cleared(self):
        """Check if customs clearance is complete."""
        return self.clearance_status == 'CLEARED'


class CustomsDeclarationLine(models.Model):
    """
    Individual line items in a customs declaration.
    Tracks HS codes, quantities, and duties per item.
    """

    customs_declaration = models.ForeignKey(
        CustomsDeclaration,
        on_delete=models.CASCADE,
        related_name='lines'
    )

    line_number = models.IntegerField(help_text="Line number in declaration")

    item = models.ForeignKey(
        'Item',
        on_delete=models.PROTECT,
        related_name='customs_lines'
    )

    # Classification
    hs_code = models.CharField(max_length=10, help_text="10-digit HS code")
    description = models.TextField(help_text="Item description for customs")
    country_of_origin = models.CharField(max_length=2, help_text="ISO country code")

    # Quantities
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_of_measure = models.CharField(max_length=10, help_text="e.g., KG, PC, M")

    # Values
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_value = models.DecimalField(max_digits=15, decimal_places=2)

    # Duties and taxes
    customs_duty_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Customs duty percentage"
    )
    customs_duty_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=VAT_RATE)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Certificates
    saber_certificate_number = models.CharField(max_length=100, blank=True)
    saso_certificate_number = models.CharField(max_length=100, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['customs_declaration', 'line_number']
        unique_together = [['customs_declaration', 'line_number']]
        verbose_name = 'Customs Declaration Line'
        verbose_name_plural = 'Customs Declaration Lines'

    def __str__(self):
        return f"Line {self.line_number}: {self.item.item_code} (HS: {self.hs_code})"

    def calculate_duties(self):
        """Calculate customs duty and VAT amounts."""
        # Customs duty
        self.customs_duty_amount = self.total_value * (self.customs_duty_rate / Decimal('100'))

        # VAT is applied on (CIF value + customs duty)
        taxable_amount = self.total_value + self.customs_duty_amount
        self.vat_amount = taxable_amount * (self.vat_rate / Decimal('100'))

        self.save()


# ==================== Shipments ====================

class Shipment(models.Model):
    """
    Track shipments and deliveries within KSA.
    Supports major Saudi carriers.
    """

    CARRIER_CHOICES = [
        ('SMSA', 'SMSA Express'),
        ('ARAMEX', 'Aramex Saudi Arabia'),
        ('DHL', 'DHL Saudi Arabia'),
        ('FEDEX', 'FedEx Saudi Arabia'),
        ('SPL', 'Saudi Post (SPL)'),
        ('UPS', 'UPS Saudi Arabia'),
        ('ZAJIL', 'Zajil Express'),
        ('NAQEL', 'Naqel Express'),
        ('OTHER', 'Other Carrier'),
    ]

    shipment_number = models.CharField(max_length=50, unique=True)
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES)
    waybill_number = models.CharField(max_length=100, help_text="Tracking/AWB number")

    # Reference
    goods_receipt = models.ForeignKey(
        'purchasing.GoodsReceipt',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='shipments'
    )

    # Addresses
    origin_address = models.TextField()
    origin_city = models.CharField(max_length=100)

    destination_address = models.TextField()
    destination_city = models.CharField(max_length=100)

    # Contact
    recipient_name = models.CharField(max_length=200)
    recipient_phone = models.CharField(max_length=20)

    # Dates
    pickup_date = models.DateField(null=True, blank=True)
    expected_delivery_date = models.DateField(null=True, blank=True)
    actual_delivery_date = models.DateField(null=True, blank=True)

    # Package details
    number_of_packages = models.IntegerField(default=1)
    total_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending Pickup'),
            ('PICKED_UP', 'Picked Up'),
            ('IN_TRANSIT', 'In Transit'),
            ('AT_HUB', 'At Distribution Hub'),
            ('OUT_FOR_DELIVERY', 'Out for Delivery'),
            ('DELIVERED', 'Delivered'),
            ('RETURNED', 'Returned to Sender'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='PENDING'
    )

    # Costs
    freight_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    insurance_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cod_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Cash on Delivery amount"
    )

    tracking_url = models.URLField(blank=True, help_text="Carrier tracking URL")
    delivered_to = models.CharField(max_length=200, blank=True, help_text="Name of person who received")

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'

    def __str__(self):
        return f"{self.shipment_number} - {self.get_carrier_display()} ({self.get_status_display()})"

    @property
    def is_delivered(self):
        """Check if shipment has been delivered."""
        return self.status == 'DELIVERED'

    @property
    def total_charges(self):
        """Calculate total shipping charges."""
        return self.freight_charges + self.insurance_charges
