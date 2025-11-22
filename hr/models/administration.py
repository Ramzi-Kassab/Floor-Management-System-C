"""
HR Administration Models - Version C
Company assets assigned to employees (phones, vehicles, housing, laptops, etc.)

Simplified from old hr_assets module.
"""
from django.db import models


ASSET_STATUS_CHOICES = [
    ('AVAILABLE', 'Available'),
    ('ASSIGNED', 'Assigned'),
    ('IN_REPAIR', 'In Repair'),
    ('RETIRED', 'Retired'),
]


class AssetType(models.Model):
    """Type of admin asset."""

    code = models.CharField(max_length=32, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    requires_serial_number = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_asset_type'
        verbose_name = 'Asset Type'
        verbose_name_plural = 'Asset Types'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class HRAsset(models.Model):
    """Company asset."""

    asset_type = models.ForeignKey(AssetType, on_delete=models.PROTECT)
    asset_number = models.CharField(max_length=64, unique=True, db_index=True)
    description = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=128, blank=True)

    # Specific fields for different asset types
    plate_number = models.CharField(max_length=32, blank=True, help_text="For vehicles")
    phone_number = models.CharField(max_length=32, blank=True, help_text="For phones")
    sim_number = models.CharField(max_length=32, blank=True, help_text="For SIM cards")
    location = models.CharField(max_length=255, blank=True, help_text="For housing/equipment")

    status = models.CharField(max_length=16, choices=ASSET_STATUS_CHOICES, default='AVAILABLE')

    # QR Integration (future)
    # asset_qr_code = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_asset'
        verbose_name = 'HR Asset'
        verbose_name_plural = 'HR Assets'
        ordering = ['asset_number']

    def __str__(self):
        return f"{self.asset_number} - {self.description}"


class AssetAssignment(models.Model):
    """Asset assignment to employee."""

    asset = models.ForeignKey(HRAsset, on_delete=models.PROTECT, related_name='assignments')
    employee = models.ForeignKey('HREmployee', on_delete=models.CASCADE, related_name='asset_assignments')
    assigned_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    condition_at_assignment = models.TextField(blank=True)
    condition_at_return = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hr_asset_assignment'
        verbose_name = 'Asset Assignment'
        verbose_name_plural = 'Asset Assignments'
        ordering = ['-assigned_date']

    def __str__(self):
        return f"{self.asset.asset_number} → {self.employee.employee_no}"
