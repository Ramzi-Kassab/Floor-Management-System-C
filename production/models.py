# -*- coding: utf-8 -*-
"""
Production Department Models for Drilling Bits Factory

This module contains comprehensive models for:
- PDC (Fixed Cutter) bits: Matrix-body and Steel-body
- Roller Cone bits
- Manufacturing workflows (New Build, Repair)
- Infiltration department (Matrix body production)
- Finishing department
- Quality Control and Evaluation
- Routing and Job Cards
- QR Code tracking
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


# ============================================================================
# CHOICES / ENUMS
# ============================================================================

class BitType(models.TextChoices):
    """Types of drilling bits manufactured"""
    PDC = 'PDC', 'PDC (Fixed Cutter)'
    ROLLER_CONE = 'ROLLER_CONE', 'Roller Cone'


class BodyMaterial(models.TextChoices):
    """Body material types for PDC bits"""
    MATRIX = 'MATRIX', 'Matrix (Infiltrated Powder)'
    STEEL = 'STEEL', 'Steel (Forged/Machined)'


class ManufacturingSource(models.TextChoices):
    """Where the bit body originated"""
    INTERNAL_MATRIX = 'INTERNAL_MATRIX', 'Internal Matrix/Infiltration'
    INTERNAL_STEEL = 'INTERNAL_STEEL', 'Internal Steel Manufacturing'
    JV_PARTIAL = 'JV_PARTIAL', 'Joint Venture Partial/Semi-finished'


class OrderType(models.TextChoices):
    """Type of work order"""
    NEW_BUILD = 'NEW_BUILD', 'New Build'
    REPAIR = 'REPAIR', 'Repair'
    EVALUATION_ONLY = 'EVALUATION_ONLY', 'Evaluation Only'


class RentOrSaleType(models.TextChoices):
    """Commercial arrangement"""
    RENTAL = 'RENTAL', 'Rental'
    SALE = 'SALE', 'Sale'
    TRIAL = 'TRIAL', 'Trial'
    WARRANTY = 'WARRANTY', 'Warranty'


class Priority(models.TextChoices):
    """Work priority levels"""
    LOW = 'LOW', 'Low'
    NORMAL = 'NORMAL', 'Normal'
    HIGH = 'HIGH', 'High'
    URGENT = 'URGENT', 'Urgent'


class WorkOrderStatus(models.TextChoices):
    """Work order lifecycle status"""
    DRAFT = 'DRAFT', 'Draft'
    OPEN = 'OPEN', 'Open'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    COMPLETED = 'COMPLETED', 'Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class JobCardStatus(models.TextChoices):
    """Job card execution status"""
    DRAFT = 'DRAFT', 'Draft'
    PLANNED = 'PLANNED', 'Planned'
    RELEASED = 'RELEASED', 'Released'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    PAUSED = 'PAUSED', 'Paused'
    QC_HOLD = 'QC_HOLD', 'QC Hold'
    COMPLETED = 'COMPLETED', 'Completed'


class Department(models.TextChoices):
    """Factory departments"""
    MATRIX_INFILTRATION = 'MATRIX_INFILTRATION', 'Matrix/Infiltration Department'
    FINISHING = 'FINISHING', 'Finishing Department'
    REPAIR = 'REPAIR', 'Repair Department'
    QC = 'QC', 'Quality Control'
    ASSEMBLY = 'ASSEMBLY', 'Assembly'


class RouteStepStatus(models.TextChoices):
    """Status of individual route steps"""
    PENDING = 'PENDING', 'Pending'
    IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
    DONE = 'DONE', 'Done'
    SKIPPED = 'SKIPPED', 'Skipped'


class InfiltrationBatchStatus(models.TextChoices):
    """Infiltration batch production status"""
    PLANNED = 'PLANNED', 'Planned'
    LOADING = 'LOADING', 'Loading'
    IN_FURNACE = 'IN_FURNACE', 'In Furnace'
    COOLING = 'COOLING', 'Cooling'
    COMPLETED = 'COMPLETED', 'Completed'
    ABORTED = 'ABORTED', 'Aborted'


class InfiltrationItemStatus(models.TextChoices):
    """Status of items in infiltration batch"""
    LOADED = 'LOADED', 'Loaded'
    IN_FURNACE = 'IN_FURNACE', 'In Furnace'
    COMPLETED = 'COMPLETED', 'Completed'
    REJECTED = 'REJECTED', 'Rejected'
    REWORK = 'REWORK', 'Rework'


class OverallCondition(models.TextChoices):
    """Overall condition assessment"""
    OK = 'OK', 'OK'
    MINOR_DAMAGE = 'MINOR_DAMAGE', 'Minor Damage'
    MAJOR_DAMAGE = 'MAJOR_DAMAGE', 'Major Damage'
    SCRAP = 'SCRAP', 'Scrap'


class RecommendedAction(models.TextChoices):
    """Recommended action after evaluation"""
    RETURN_AS_IS = 'RETURN_AS_IS', 'Return As-Is'
    REPAIR = 'REPAIR', 'Repair'
    SCRAP = 'SCRAP', 'Scrap'


class NDTMethod(models.TextChoices):
    """Non-Destructive Testing methods"""
    MPI = 'MPI', 'Magnetic Particle Inspection'
    DPI = 'DPI', 'Dye Penetrant Inspection'
    UT = 'UT', 'Ultrasonic Testing'
    RT = 'RT', 'Radiographic Testing'
    VT = 'VT', 'Visual Testing'


class InspectionResult(models.TextChoices):
    """Inspection result values"""
    PASS = 'PASS', 'Pass'
    FAIL = 'FAIL', 'Fail'
    CONDITIONAL = 'CONDITIONAL', 'Conditional'
    REWORK = 'REWORK', 'Rework'
    REJECT = 'REJECT', 'Reject'


class BitInstanceStatus(models.TextChoices):
    """Current status of a bit instance"""
    IN_STOCK = 'IN_STOCK', 'In Stock'
    WITH_CUSTOMER = 'WITH_CUSTOMER', 'With Customer'
    IN_REPAIR = 'IN_REPAIR', 'In Repair'
    SCRAPPED = 'SCRAPPED', 'Scrapped'
    IN_PRODUCTION = 'IN_PRODUCTION', 'In Production'


# ============================================================================
# BIT DESIGN & INSTANCES
# ============================================================================

class BitDesign(models.Model):
    """
    Core bit design/blueprint for Fixed Cutter (PDC) bits

    Represents the engineering design of a bit. For PDC bits, includes
    comprehensive design parameters. For Roller Cone, basic fields only
    (detailed RC fields will be in separate model later).

    Field Order (for forms):
    1. Bit Category (bit_type)
    2. Size (size_inch)
    3. Current SMI Name (current_smi_name)
    4. HDBS Name (hdbs_name)
    5. IADC Code (iadc_code)
    6. Body Material
    7. Blade Count
    8. Cutter Size Category
    9. Gauge Length
    10. Nozzle Count
    11. Port Count
    12. Connection Type
    13. Description (auto-generated)
    14. Remarks (free text notes)
    """
    # 1. Bit Category - FIRST FIELD
    bit_type = models.CharField(
        max_length=20,
        choices=BitType.choices,
        help_text="Bit Category: Fixed Cutter (PDC) or Roller Cone",
        verbose_name="Bit Category (Bit Cat)"
    )

    # 2. Size
    size_inch = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        help_text="Bit diameter in inches (e.g., 8.5, 12.25)"
    )

    # 3. Current SMI Name
    current_smi_name = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="ARDT / SMI type (e.g., HD75WF, MMD53DH-2)",
        verbose_name="Current SMI Name"
    )

    # 4. HDBS Name
    hdbs_name = models.CharField(
        max_length=50,
        blank=True,
        db_index=True,
        help_text="Halliburton design name (e.g., MMD53DH, SF53, EQH12R)",
        verbose_name="HDBS Name"
    )

    # 5. IADC Code
    iadc_code = models.CharField(
        max_length=10,
        blank=True,
        db_index=True,
        help_text="IADC bit code (e.g., S334, M223, 437, 111)",
        verbose_name="IADC Code"
    )

    # Legacy design_code (keep for backward compatibility)
    design_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique design code (typically same as current_smi_name or hdbs_name)"
    )

    # 6. Body Material
    body_material = models.CharField(
        max_length=20,
        choices=BodyMaterial.choices,
        blank=True,
        null=True,
        help_text="Body material (Matrix or Steel) - auto-derived from name if empty"
    )

    # 7. Blade Count
    blade_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of blades (for PDC bits) - auto-derived from name if empty"
    )

    # 8. Cutter Size Category
    cutter_size_category = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(3), MaxValueValidator(8)],
        help_text="Cutter size category (3-8) - auto-derived from name if empty"
    )

    # 9. Gauge Length
    gauge_length_inch = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Gauge length in inches",
        verbose_name="Gauge Length (inch)"
    )

    # 10. Nozzle Count
    nozzle_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of nozzles"
    )

    # 11. Port Count (NEW)
    port_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of ports (can differ from nozzle count)"
    )

    # 12. Connection Type
    connection_type = models.CharField(
        max_length=30,
        blank=True,
        choices=[
            ('REGULAR', 'Regular'),
            ('CEREBRO', 'Cerebro'),
            ('WITH_EROSION_SLEEVE', 'With Erosion Sleeve'),
            ('SHANKLESS', 'Shankless'),
            ('OTHER', 'Other'),
        ],
        help_text="Type of connection"
    )

    # 13. Description (auto-generated)
    description = models.TextField(
        blank=True,
        help_text="Auto-generated: {size}-{name}-{iadc}. Can be edited manually."
    )

    # 14. Remarks (NEW - free text notes)
    remarks = models.TextField(
        blank=True,
        help_text="Free-text human comments and notes about the design"
    )

    # Metadata
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Is this design currently active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['bit_type', 'size_inch', 'current_smi_name']
        indexes = [
            models.Index(fields=['bit_type', 'active']),
            models.Index(fields=['size_inch']),
            models.Index(fields=['current_smi_name']),
            models.Index(fields=['hdbs_name']),
            models.Index(fields=['iadc_code']),
        ]

    def __str__(self):
        name = self.current_smi_name or self.hdbs_name or self.design_code
        return f"{self.size_inch}\" - {name} ({self.get_bit_type_display()})"

    def save(self, *args, **kwargs):
        """
        Auto-fill logic for PDC/Fixed Cutter bits:
        1. Derive body material, blades, cutter size from design name
        2. Auto-generate description
        """
        # Only auto-fill for PDC bits
        if self.bit_type == BitType.PDC:
            # Get the design name (prefer current_smi_name, fallback to hdbs_name)
            design_name = self.current_smi_name or self.hdbs_name or ''

            if design_name:
                # 1. Auto-derive body material if empty
                if not self.body_material:
                    # If name starts or ends with 'S', default to Steel
                    if design_name.upper().startswith('S') or design_name.upper().endswith('S'):
                        self.body_material = BodyMaterial.STEEL
                    else:
                        self.body_material = BodyMaterial.MATRIX

                # 2. Auto-derive blade count from first digit (if empty)
                if not self.blade_count and design_name:
                    # Find first digit in name
                    for char in design_name:
                        if char.isdigit():
                            self.blade_count = int(char)
                            break

                # 3. Auto-derive cutter size category from second digit (if empty)
                if not self.cutter_size_category and design_name:
                    # Find second digit in name
                    digit_count = 0
                    for char in design_name:
                        if char.isdigit():
                            digit_count += 1
                            if digit_count == 2:
                                cutter_cat = int(char)
                                # Validate range 3-8
                                if 3 <= cutter_cat <= 8:
                                    self.cutter_size_category = cutter_cat
                                break

            # 4. Auto-generate description if empty
            if not self.description:
                name = self.current_smi_name or self.hdbs_name or self.design_code
                iadc = self.iadc_code or ''
                self.description = f"{self.size_inch}-{name}-{iadc}".rstrip('-')

        # Call parent save
        super().save(*args, **kwargs)


class BitDesignRevision(models.Model):
    """
    Design revisions with MAT numbers (Level 3/4/5)
    Tracks engineering changes and material specifications
    """
    design = models.ForeignKey(
        BitDesign,
        on_delete=models.CASCADE,
        related_name='revisions'
    )
    mat_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Material/Manufacturing number (MAT number)"
    )
    level = models.PositiveIntegerField(
        help_text="MAT level (3, 4, 5, etc.)"
    )
    effective_from = models.DateField(
        help_text="Date this revision becomes effective"
    )
    effective_to = models.DateField(
        blank=True,
        null=True,
        help_text="Date this revision expires (null = current)"
    )
    active = models.BooleanField(
        default=True,
        db_index=True
    )
    remarks = models.TextField(
        blank=True,
        help_text="Revision notes and changes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-effective_from', 'mat_number']
        indexes = [
            models.Index(fields=['design', 'active']),
            models.Index(fields=['effective_from', 'effective_to']),
        ]
        verbose_name_plural = 'Bit design revisions'

    def __str__(self):
        return f"{self.mat_number} (Level {self.level}) - {self.design.design_code}"


class BitInstance(models.Model):
    """
    Physical bit with serial number
    Tracks individual bits through manufacturing, sales, and repairs
    """
    serial_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Base serial number (without R1/R2 suffix)"
    )
    design_revision = models.ForeignKey(
        BitDesignRevision,
        on_delete=models.PROTECT,
        related_name='instances',
        help_text="Design revision/MAT number for this bit"
    )
    body_material = models.CharField(
        max_length=20,
        choices=BodyMaterial.choices,
        help_text="Actual body material used"
    )
    manufacturing_source = models.CharField(
        max_length=30,
        choices=ManufacturingSource.choices,
        help_text="Where the body originated"
    )
    initial_build_wo = models.ForeignKey(
        'WorkOrder',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='built_bits',
        help_text="Initial build work order"
    )
    current_repair_index = models.PositiveIntegerField(
        default=0,
        help_text="Repair count: 0=new, 1=R1, 2=R2, etc."
    )
    status = models.CharField(
        max_length=20,
        choices=BitInstanceStatus.choices,
        default=BitInstanceStatus.IN_PRODUCTION,
        db_index=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'manufacturing_source']),
            models.Index(fields=['design_revision', 'body_material']),
        ]

    def __str__(self):
        repair_suffix = f"-R{self.current_repair_index}" if self.current_repair_index > 0 else ""
        return f"{self.serial_number}{repair_suffix}"

    def get_full_serial(self):
        """Get serial with repair suffix if applicable"""
        if self.current_repair_index > 0:
            return f"{self.serial_number}-R{self.current_repair_index}"
        return self.serial_number

    def get_all_work_orders(self):
        """Get all work orders for this bit (initial build + all repairs)"""
        return self.work_orders.all().order_by('created_at')

    def get_repair_history_chain(self):
        """Get complete repair history in chronological order"""
        return self.repair_history.all().order_by('repair_index')

    def get_last_repair(self):
        """Get the most recent repair record"""
        return self.repair_history.filter(
            repair_index=self.current_repair_index
        ).first() if self.current_repair_index > 0 else None

    def get_total_repairs_count(self):
        """Get total number of repairs performed"""
        return self.current_repair_index

    def can_be_repaired_again(self):
        """Check if bit can be repaired again (business logic)"""
        # Example: Maximum 5 repairs allowed
        return self.current_repair_index < 5 and self.status != 'SCRAPPED'


# ============================================================================
# WORK ORDERS & JOB CARDS
# ============================================================================

class WorkOrder(models.Model):
    """
    High-level manufacturing/repair order
    Connected to customers and planning
    """
    wo_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Human-readable work order number"
    )
    order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        db_index=True
    )
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='work_orders',
        help_text="Existing bit (for repairs) or null for new builds"
    )
    design_revision = models.ForeignKey(
        BitDesignRevision,
        on_delete=models.PROTECT,
        related_name='work_orders',
        help_text="Planned design/MAT for this order"
    )
    customer_name = models.CharField(max_length=200)
    rig = models.CharField(max_length=100, blank=True)
    well = models.CharField(max_length=100, blank=True)
    field = models.CharField(max_length=100, blank=True)
    rent_or_sale_type = models.CharField(
        max_length=20,
        choices=RentOrSaleType.choices,
        blank=True
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=WorkOrderStatus.choices,
        default=WorkOrderStatus.DRAFT,
        db_index=True
    )
    received_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date bit/order was received"
    )
    due_date = models.DateField(
        blank=True,
        null=True,
        help_text="Target completion date"
    )
    remarks = models.TextField(blank=True)
    external_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="External system reference (ERP, etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['order_type', 'status']),
            models.Index(fields=['customer_name']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"WO-{self.wo_number} ({self.get_order_type_display()})"


class JobCard(models.Model):
    """
    Shop floor job card - what operators see and scan
    Linked to work orders, tracks actual execution
    """
    jobcard_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique job card code (used in QR codes)"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='job_cards'
    )
    job_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        help_text="Derived from work order"
    )
    is_repair = models.BooleanField(
        default=False,
        help_text="Is this a repair job?"
    )
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        blank=True,
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=JobCardStatus.choices,
        default=JobCardStatus.DRAFT,
        db_index=True
    )
    planned_start = models.DateTimeField(blank=True, null=True)
    planned_end = models.DateTimeField(blank=True, null=True)
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)
    current_workstation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current workstation/machine"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'department']),
            models.Index(fields=['work_order', 'status']),
        ]

    def __str__(self):
        return f"JC-{self.jobcard_code}"


# ============================================================================
# ROUTING & EXECUTION
# ============================================================================

class RouteTemplate(models.Model):
    """
    Predefined workflow template for different bit types and operations
    """
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Route template name (e.g., 'PDC Matrix New Build 12.25')"
    )
    bit_type = models.CharField(
        max_length=20,
        choices=BitType.choices
    )
    body_material = models.CharField(
        max_length=20,
        choices=BodyMaterial.choices,
        blank=True
    )
    for_order_type = models.CharField(
        max_length=20,
        choices=OrderType.choices,
        help_text="NEW_BUILD, REPAIR, or ANY"
    )
    department_focus = models.CharField(
        max_length=30,
        choices=Department.choices,
        blank=True,
        help_text="Primary department for this route"
    )
    active = models.BooleanField(default=True, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['bit_type', 'active']),
            models.Index(fields=['for_order_type', 'active']),
        ]

    def __str__(self):
        return self.name


class RouteStepTemplate(models.Model):
    """
    Individual step within a route template
    """
    route = models.ForeignKey(
        RouteTemplate,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    sequence = models.PositiveIntegerField(
        help_text="Order of execution"
    )
    process_code = models.CharField(
        max_length=100,
        help_text="Process identifier (e.g., INFILTRATION, MACHINING, BRAZING)"
    )
    description = models.TextField(
        help_text="Detailed step description"
    )
    default_department = models.CharField(
        max_length=30,
        choices=Department.choices,
        blank=True
    )
    default_workstation = models.CharField(
        max_length=100,
        blank=True
    )
    estimated_duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Estimated time to complete (minutes)"
    )
    is_mandatory = models.BooleanField(
        default=True,
        help_text="Must this step be completed?"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['route', 'sequence']
        unique_together = [['route', 'sequence']]
        indexes = [
            models.Index(fields=['route', 'sequence']),
        ]

    def __str__(self):
        return f"{self.route.name} - Step {self.sequence}: {self.process_code}"


class JobRouteStep(models.Model):
    """
    Actual execution of a route step for a specific job card
    """
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='route_steps'
    )
    template = models.ForeignKey(
        RouteStepTemplate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Template this step was created from"
    )
    sequence = models.PositiveIntegerField()
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        blank=True
    )
    workstation = models.CharField(max_length=100, blank=True)
    process_code = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=RouteStepStatus.choices,
        default=RouteStepStatus.PENDING,
        db_index=True
    )
    planned_start = models.DateTimeField(blank=True, null=True)
    planned_end = models.DateTimeField(blank=True, null=True)
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='route_steps'
    )
    operator_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Operator name if not linked to User"
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['job_card', 'sequence']
        unique_together = [['job_card', 'sequence']]
        indexes = [
            models.Index(fields=['job_card', 'status']),
            models.Index(fields=['status', 'department']),
        ]

    def __str__(self):
        return f"{self.job_card.jobcard_code} - Step {self.sequence}: {self.process_code}"


class JobPause(models.Model):
    """
    Track pauses/holds during job execution
    """
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='pauses'
    )
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)
    reason = models.CharField(
        max_length=200,
        help_text="e.g., Waiting material, Waiting QC, Machine breakdown"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['job_card', 'start_time']),
        ]

    def __str__(self):
        duration = "ongoing" if not self.end_time else f"{(self.end_time - self.start_time).total_seconds() / 3600:.1f}h"
        return f"{self.job_card.jobcard_code} - Pause: {self.reason} ({duration})"


# ============================================================================
# INFILTRATION / MATRIX PRODUCTION
# ============================================================================

class InfiltrationBatch(models.Model):
    """
    Batch production for matrix bodies using infiltration furnaces
    """
    batch_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique batch identifier"
    )
    furnace_id = models.CharField(
        max_length=50,
        help_text="Furnace identifier"
    )
    planned_start = models.DateTimeField()
    planned_end = models.DateTimeField()
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)
    temperature_profile = models.TextField(
        blank=True,
        help_text="Temperature profile settings (can be JSON)"
    )
    operator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='infiltration_batches'
    )
    operator_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(
        max_length=20,
        choices=InfiltrationBatchStatus.choices,
        default=InfiltrationBatchStatus.PLANNED,
        db_index=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'furnace_id']),
            models.Index(fields=['planned_start']),
        ]
        verbose_name_plural = 'Infiltration batches'

    def __str__(self):
        return f"Batch {self.batch_code} ({self.furnace_id})"


class InfiltrationBatchItem(models.Model):
    """
    Individual matrix body in an infiltration batch
    """
    batch = models.ForeignKey(
        InfiltrationBatch,
        on_delete=models.CASCADE,
        related_name='items'
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='infiltration_items',
        help_text="Job card for the matrix body being produced"
    )
    mold_id = models.CharField(
        max_length=50,
        help_text="Mold identifier"
    )
    powder_mix_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="Powder mixture specification"
    )
    status = models.CharField(
        max_length=20,
        choices=InfiltrationItemStatus.choices,
        default=InfiltrationItemStatus.LOADED
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['batch', 'id']
        indexes = [
            models.Index(fields=['batch', 'status']),
        ]

    def __str__(self):
        return f"{self.batch.batch_code} - {self.job_card.jobcard_code} (Mold: {self.mold_id})"


# ============================================================================
# QUALITY CONTROL & EVALUATION
# ============================================================================

class EvaluationSummary(models.Model):
    """
    Overall evaluation of returned bits (for repairs)
    """
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='evaluations'
    )
    evaluation_date = models.DateField(default=timezone.now)
    evaluator_name = models.CharField(max_length=100)
    overall_condition = models.CharField(
        max_length=20,
        choices=OverallCondition.choices
    )
    recommended_action = models.CharField(
        max_length=20,
        choices=RecommendedAction.choices
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-evaluation_date']
        verbose_name_plural = 'Evaluation summaries'

    def __str__(self):
        return f"Eval: {self.job_card.jobcard_code} - {self.get_overall_condition_display()}"


class NDTResult(models.Model):
    """
    Non-Destructive Testing results
    """
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='ndt_results'
    )
    method = models.CharField(
        max_length=20,
        choices=NDTMethod.choices,
        help_text="NDT method used"
    )
    result = models.CharField(
        max_length=20,
        choices=InspectionResult.choices
    )
    inspector_name = models.CharField(max_length=100)
    performed_at = models.DateTimeField(default=timezone.now)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['job_card', 'method']),
        ]

    def __str__(self):
        return f"NDT-{self.get_method_display()}: {self.job_card.jobcard_code} - {self.get_result_display()}"


class ThreadInspectionResult(models.Model):
    """
    Thread inspection results (API, premium connections)
    """
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='thread_inspections'
    )
    connection_type = models.CharField(
        max_length=100,
        help_text="e.g., API, premium thread type"
    )
    result = models.CharField(
        max_length=20,
        choices=InspectionResult.choices
    )
    gauge_used = models.CharField(
        max_length=100,
        blank=True,
        help_text="Thread gauge identifier"
    )
    inspector_name = models.CharField(max_length=100)
    performed_at = models.DateTimeField(default=timezone.now)
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-performed_at']
        indexes = [
            models.Index(fields=['job_card', 'result']),
        ]

    def __str__(self):
        return f"Thread: {self.job_card.jobcard_code} - {self.get_result_display()}"


# ============================================================================
# QR CODES
# ============================================================================

class QRCode(models.Model):
    """
    QR codes for shop floor tracking
    Can link to job cards or route steps
    """
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        default=uuid.uuid4,
        help_text="Unique code encoded in QR"
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='qr_codes'
    )
    route_step = models.ForeignKey(
        JobRouteStep,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='qr_codes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Optional expiration date"
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'QR Code'
        verbose_name_plural = 'QR Codes'

    def __str__(self):
        if self.job_card:
            return f"QR: {self.code} -> {self.job_card.jobcard_code}"
        elif self.route_step:
            return f"QR: {self.code} -> Step {self.route_step.sequence}"
        return f"QR: {self.code}"

    def get_target(self):
        """Get the target object this QR code points to"""
        if self.job_card:
            return self.job_card
        elif self.route_step:
            return self.route_step
        return None


# ============================================================================
# NON-CONFORMANCE & QUALITY MANAGEMENT
# ============================================================================

class NCRSeverity(models.TextChoices):
    """Non-conformance severity levels"""
    MINOR = 'MINOR', 'Minor'
    MAJOR = 'MAJOR', 'Major'
    CRITICAL = 'CRITICAL', 'Critical'


class NCRStatus(models.TextChoices):
    """Non-conformance report status"""
    OPEN = 'OPEN', 'Open'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    PENDING_MRB = 'PENDING_MRB', 'Pending MRB Decision'
    CLOSED = 'CLOSED', 'Closed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class DispositionType(models.TextChoices):
    """Material Review Board disposition decisions"""
    USE_AS_IS = 'USE_AS_IS', 'Use As-Is'
    USE_AS_IS_WITH_DEVIATION = 'USE_AS_IS_DEVIATION', 'Use As-Is with Deviation'
    REWORK = 'REWORK', 'Rework'
    REPAIR = 'REPAIR', 'Repair'
    SCRAP = 'SCRAP', 'Scrap'
    RETURN_TO_SUPPLIER = 'RETURN_SUPPLIER', 'Return to Supplier'
    DOWNGRADE = 'DOWNGRADE', 'Downgrade'


class ScrapReason(models.TextChoices):
    """Reasons for scrapping"""
    QUALITY_FAILURE = 'QUALITY_FAILURE', 'Quality Failure'
    MATERIAL_DEFECT = 'MATERIAL_DEFECT', 'Material Defect'
    MANUFACTURING_ERROR = 'MFG_ERROR', 'Manufacturing Error'
    DAMAGE_IN_PROCESS = 'DAMAGE_PROCESS', 'Damage in Process'
    DESIGN_OBSOLETE = 'DESIGN_OBSOLETE', 'Design Obsolete'
    CUSTOMER_REJECTION = 'CUSTOMER_REJECT', 'Customer Rejection'
    EXCESSIVE_WEAR = 'EXCESSIVE_WEAR', 'Excessive Wear (Repair not economical)'
    INFILTRATION_FAILURE = 'INFILTRATION_FAIL', 'Infiltration Failure'
    BRAZE_FAILURE = 'BRAZE_FAILURE', 'Brazing Failure'
    CRACK_DETECTED = 'CRACK_DETECTED', 'Crack Detected (NDT)'
    OTHER = 'OTHER', 'Other'


class ReworkReason(models.TextChoices):
    """Reasons for rework"""
    DIMENSION_OUT_SPEC = 'DIM_OUT_SPEC', 'Dimension Out of Specification'
    SURFACE_FINISH = 'SURFACE_FINISH', 'Surface Finish Issues'
    THREAD_ISSUES = 'THREAD_ISSUES', 'Thread Quality Issues'
    INCOMPLETE_BRAZING = 'INCOMPLETE_BRAZE', 'Incomplete Brazing'
    HARDFACING_DEFECT = 'HARDFACING_DEFECT', 'Hardfacing Defect'
    WELDING_DEFECT = 'WELD_DEFECT', 'Welding Defect'
    CONTAMINATION = 'CONTAMINATION', 'Contamination'
    INCOMPLETE_PROCESS = 'INCOMPLETE_PROC', 'Incomplete Process Step'
    COSMETIC = 'COSMETIC', 'Cosmetic (Customer Requirement)'
    OTHER = 'OTHER', 'Other'


class HoldReason(models.TextChoices):
    """Reasons for production holds"""
    WAITING_MATERIAL = 'WAIT_MATERIAL', 'Waiting for Material'
    WAITING_QC = 'WAIT_QC', 'Waiting for QC/Inspection'
    WAITING_ENGINEERING = 'WAIT_ENG', 'Waiting for Engineering Decision'
    MACHINE_BREAKDOWN = 'MACHINE_DOWN', 'Machine Breakdown'
    TOOL_UNAVAILABLE = 'TOOL_UNAVAIL', 'Tool/Fixture Unavailable'
    CUSTOMER_HOLD = 'CUSTOMER_HOLD', 'Customer Hold'
    QUALITY_ISSUE = 'QUALITY_ISSUE', 'Quality Issue Under Investigation'
    DESIGN_CHANGE = 'DESIGN_CHANGE', 'Design Change Pending'
    OPERATOR_UNAVAILABLE = 'NO_OPERATOR', 'Operator Unavailable'
    FURNACE_UNAVAILABLE = 'FURNACE_UNAVAIL', 'Furnace Unavailable'
    POWER_OUTAGE = 'POWER_OUTAGE', 'Power Outage'
    OTHER = 'OTHER', 'Other'


class NonConformanceReport(models.Model):
    """
    NCR - Track quality issues, defects, and non-conformances
    """
    ncr_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique NCR number (e.g., NCR-2025-001)"
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='ncrs',
        blank=True,
        null=True,
        help_text="Related job card (if applicable)"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='ncrs',
        blank=True,
        null=True,
        help_text="Related work order"
    )
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='ncrs',
        help_text="Affected bit instance"
    )
    severity = models.CharField(
        max_length=20,
        choices=NCRSeverity.choices,
        default=NCRSeverity.MINOR
    )
    status = models.CharField(
        max_length=20,
        choices=NCRStatus.choices,
        default=NCRStatus.OPEN,
        db_index=True
    )
    detected_at_process = models.CharField(
        max_length=100,
        help_text="Process where issue was detected (e.g., BRAZING, NDT_INSPECTION)"
    )
    detected_by = models.CharField(max_length=100)
    detected_date = models.DateTimeField(default=timezone.now)
    
    description = models.TextField(
        help_text="Detailed description of the non-conformance"
    )
    root_cause = models.TextField(
        blank=True,
        help_text="Root cause analysis (filled after investigation)"
    )
    corrective_action = models.TextField(
        blank=True,
        help_text="Corrective action taken or planned"
    )
    preventive_action = models.TextField(
        blank=True,
        help_text="Preventive action to avoid recurrence"
    )
    
    # Disposition (MRB decision)
    disposition = models.CharField(
        max_length=30,
        choices=DispositionType.choices,
        blank=True,
        help_text="MRB disposition decision"
    )
    disposition_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date of MRB decision"
    )
    disposition_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="Person who made disposition decision"
    )
    disposition_notes = models.TextField(
        blank=True,
        help_text="Disposition justification and notes"
    )
    
    # Closure
    closed_date = models.DateTimeField(blank=True, null=True)
    closed_by = models.CharField(max_length=100, blank=True)
    
    # Costs
    estimated_cost_impact = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Estimated cost impact (USD)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['detected_date']),
        ]
        verbose_name = 'Non-Conformance Report'
        verbose_name_plural = 'Non-Conformance Reports'

    def __str__(self):
        return f"{self.ncr_number} - {self.get_severity_display()}"


class ScrapRecord(models.Model):
    """
    Track scrapped bits and components with reasons and costs
    """
    scrap_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique scrap record number"
    )
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='scrap_records',
        help_text="Scrapped bit instance"
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='scrap_records',
        blank=True,
        null=True
    )
    ncr = models.ForeignKey(
        NonConformanceReport,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='scrap_records',
        help_text="Related NCR if applicable"
    )
    
    scrap_reason = models.CharField(
        max_length=30,
        choices=ScrapReason.choices,
        db_index=True
    )
    scrap_date = models.DateTimeField(default=timezone.now)
    
    item_description = models.CharField(
        max_length=200,
        help_text="What was scrapped (e.g., 'Complete bit', 'Matrix body', '12 PDC cutters')"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.0,
        help_text="Quantity scrapped"
    )
    unit = models.CharField(
        max_length=20,
        default='EA',
        help_text="Unit of measure (EA, KG, etc.)"
    )
    
    # Cost tracking
    material_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Material cost lost (USD)"
    )
    labor_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Labor cost invested (USD)"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total cost impact (USD)"
    )
    
    # Approval
    approved_by = models.CharField(
        max_length=100,
        help_text="Manager/supervisor who approved scrap"
    )
    approval_date = models.DateTimeField(default=timezone.now)
    
    # Recovery
    salvage_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Salvage/recovery value (USD)"
    )
    salvage_notes = models.TextField(
        blank=True,
        help_text="Notes on material recovery (e.g., cutters salvaged, metal recycled)"
    )
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scrap_date']
        indexes = [
            models.Index(fields=['scrap_date']),
            models.Index(fields=['scrap_reason']),
        ]
        verbose_name = 'Scrap Record'
        verbose_name_plural = 'Scrap Records'

    def __str__(self):
        return f"{self.scrap_number} - {self.item_description}"


class ReworkRecord(models.Model):
    """
    Track rework operations with reasons, costs, and history
    """
    rework_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique rework record number"
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='rework_records'
    )
    ncr = models.ForeignKey(
        NonConformanceReport,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='rework_records'
    )
    
    rework_reason = models.CharField(
        max_length=30,
        choices=ReworkReason.choices,
        db_index=True
    )
    original_process = models.CharField(
        max_length=100,
        help_text="Original process that needs rework (e.g., BRAZING, THREAD_CUTTING)"
    )
    
    rework_description = models.TextField(
        help_text="Detailed description of rework required"
    )
    rework_instructions = models.TextField(
        help_text="Specific rework instructions"
    )
    
    # Scheduling
    planned_start = models.DateTimeField(blank=True, null=True)
    planned_end = models.DateTimeField(blank=True, null=True)
    actual_start = models.DateTimeField(blank=True, null=True)
    actual_end = models.DateTimeField(blank=True, null=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='rework_assignments'
    )
    assigned_to_name = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed (Re-scrap)'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='PENDING',
        db_index=True
    )
    
    # Verification
    verified_by = models.CharField(max_length=100, blank=True)
    verified_date = models.DateTimeField(blank=True, null=True)
    verification_notes = models.TextField(blank=True)
    
    # Costs
    labor_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Labor hours spent on rework"
    )
    material_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Additional material cost for rework (USD)"
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total rework cost (USD)"
    )
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'rework_reason']),
            models.Index(fields=['actual_start']),
        ]
        verbose_name = 'Rework Record'
        verbose_name_plural = 'Rework Records'

    def __str__(self):
        return f"{self.rework_number} - {self.get_rework_reason_display()}"


class ProductionHold(models.Model):
    """
    Enhanced production hold tracking with detailed reasons and approvals
    """
    hold_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique hold identifier"
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='production_holds'
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='production_holds',
        blank=True,
        null=True
    )
    
    hold_reason = models.CharField(
        max_length=30,
        choices=HoldReason.choices,
        db_index=True
    )
    hold_initiated_by = models.CharField(max_length=100)
    hold_start = models.DateTimeField(default=timezone.now)
    hold_end = models.DateTimeField(blank=True, null=True)
    
    description = models.TextField(
        help_text="Detailed description of hold reason"
    )
    resolution = models.TextField(
        blank=True,
        help_text="How the hold was resolved"
    )
    
    # For customer holds or design changes - require approval to release
    requires_approval = models.BooleanField(
        default=False,
        help_text="Does this hold require management approval to release?"
    )
    approved_for_release_by = models.CharField(max_length=100, blank=True)
    approval_date = models.DateTimeField(blank=True, null=True)
    
    # Impact tracking
    estimated_delay_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Estimated production delay in hours"
    )
    cost_impact = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Estimated cost impact (USD)"
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('ACTIVE', 'Active'),
            ('RELEASED', 'Released'),
            ('CANCELLED', 'Cancelled'),
        ],
        default='ACTIVE',
        db_index=True
    )
    
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-hold_start']
        indexes = [
            models.Index(fields=['status', 'hold_reason']),
            models.Index(fields=['hold_start']),
        ]
        verbose_name = 'Production Hold'
        verbose_name_plural = 'Production Holds'

    def __str__(self):
        duration = "ongoing" if not self.hold_end else f"{(self.hold_end - self.hold_start).total_seconds() / 3600:.1f}h"
        return f"{self.hold_number} - {self.get_hold_reason_display()} ({duration})"

    def get_duration_hours(self):
        """Calculate hold duration in hours"""
        if self.hold_end:
            return (self.hold_end - self.hold_start).total_seconds() / 3600
        else:
            return (timezone.now() - self.hold_start).total_seconds() / 3600


# ============================================================================
# EMPLOYEE MANAGEMENT
# ============================================================================

class EmployeeRole(models.TextChoices):
    """Employee roles in production"""
    OPERATOR = 'OPERATOR', 'Machine Operator'
    TECHNICIAN = 'TECHNICIAN', 'Technician'
    QC_INSPECTOR = 'QC_INSPECTOR', 'QC Inspector'
    SUPERVISOR = 'SUPERVISOR', 'Supervisor'
    ENGINEER = 'ENGINEER', 'Engineer'
    MANAGER = 'MANAGER', 'Manager'


class EmployeeStatus(models.TextChoices):
    """Employee employment status"""
    ACTIVE = 'ACTIVE', 'Active'
    ON_LEAVE = 'ON_LEAVE', 'On Leave'
    INACTIVE = 'INACTIVE', 'Inactive'


class Employee(models.Model):
    """
    Employee/Worker in production department
    Links to Django User for authentication
    """
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='employee_profile',
        help_text="Linked user account (optional)"
    )
    employee_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique employee ID (e.g., EMP001)"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        db_index=True,
        help_text="Primary department assignment"
    )
    role = models.CharField(
        max_length=20,
        choices=EmployeeRole.choices,
        default=EmployeeRole.OPERATOR
    )
    status = models.CharField(
        max_length=20,
        choices=EmployeeStatus.choices,
        default=EmployeeStatus.ACTIVE,
        db_index=True
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        db_index=True,
        help_text="Phone number for operator recognition (unique)"
    )
    email = models.EmailField(blank=True)
    hire_date = models.DateField(help_text="Employment start date")
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated list of skills/certifications"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['department', 'status']),
            models.Index(fields=['role', 'status']),
        ]

    def __str__(self):
        return f"{self.employee_code} - {self.first_name} {self.last_name} ({self.get_department_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


# ============================================================================
# BIT RECEIVING & RELEASE
# ============================================================================

class ReceiveInspectionStatus(models.TextChoices):
    """Status of receiving inspection"""
    PENDING = 'PENDING', 'Pending Inspection'
    IN_PROGRESS = 'IN_PROGRESS', 'Inspection In Progress'
    PASSED = 'PASSED', 'Passed'
    FAILED = 'FAILED', 'Failed'
    CONDITIONAL = 'CONDITIONAL', 'Conditional Accept'


class BitLocationStatus(models.TextChoices):
    """Current location/status of a bit"""
    IN_TRANSIT_RECEIVING = 'IN_TRANSIT_RECEIVING', 'In Transit (Receiving)'
    RECEIVING_INSPECTION = 'RECEIVING_INSPECTION', 'Receiving Inspection'
    IN_PRODUCTION = 'IN_PRODUCTION', 'In Production'
    QC_HOLD = 'QC_HOLD', 'QC Hold'
    READY_FOR_RELEASE = 'READY_FOR_RELEASE', 'Ready for Release'
    IN_TRANSIT_SHIPPING = 'IN_TRANSIT_SHIPPING', 'In Transit (Shipping)'
    WITH_CUSTOMER = 'WITH_CUSTOMER', 'With Customer'
    SCRAPPED = 'SCRAPPED', 'Scrapped'


class ReleaseStatus(models.TextChoices):
    """Status of bit release/dispatch"""
    DRAFT = 'DRAFT', 'Draft'
    READY = 'READY', 'Ready for Dispatch'
    DISPATCHED = 'DISPATCHED', 'Dispatched'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'


class BitReceive(models.Model):
    """
    Record of drill bit receiving into facility
    For both new builds (raw materials) and repairs (returning bits)
    """
    receive_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique receive transaction number (e.g., RCV-2025-001)"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='receives',
        help_text="Associated work order"
    )
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='receives',
        help_text="Bit instance (for repairs)"
    )
    received_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date/time bit was received"
    )
    received_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='received_bits',
        help_text="Employee who received the bit"
    )
    received_by_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name if not linked to Employee"
    )
    customer_name = models.CharField(max_length=200)
    transport_company = models.CharField(
        max_length=200,
        blank=True,
        help_text="Shipping/transport company"
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shipment tracking number"
    )

    # Physical condition on arrival
    package_condition = models.CharField(
        max_length=20,
        choices=[
            ('GOOD', 'Good'),
            ('DAMAGED', 'Damaged'),
            ('POOR', 'Poor')
        ],
        default='GOOD',
        help_text="Condition of packaging"
    )

    # Inspection
    inspection_status = models.CharField(
        max_length=20,
        choices=ReceiveInspectionStatus.choices,
        default=ReceiveInspectionStatus.PENDING,
        db_index=True
    )
    inspected_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='inspected_receives',
        help_text="QC inspector"
    )
    inspection_date = models.DateTimeField(blank=True, null=True)
    inspection_notes = models.TextField(
        blank=True,
        help_text="Initial inspection observations"
    )

    # Accompanying documentation
    customer_po = models.CharField(
        max_length=100,
        blank=True,
        help_text="Customer PO number"
    )
    packing_slip = models.CharField(
        max_length=100,
        blank=True,
        help_text="Packing slip number"
    )
    has_bit_record = models.BooleanField(
        default=False,
        help_text="Did bit arrive with usage/drilling record?"
    )

    # Photos/attachments (file paths)
    photo_paths = models.TextField(
        blank=True,
        help_text="JSON array of photo file paths"
    )

    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-received_date']
        indexes = [
            models.Index(fields=['inspection_status', 'received_date']),
            models.Index(fields=['work_order', 'received_date']),
        ]
        verbose_name = 'Bit Receive'
        verbose_name_plural = 'Bit Receives'

    def __str__(self):
        return f"{self.receive_number} - {self.customer_name} ({self.received_date.strftime('%Y-%m-%d')})"


class BitRelease(models.Model):
    """
    Record of drill bit release/dispatch to customer
    """
    release_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique release transaction number (e.g., REL-2025-001)"
    )
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='releases',
        help_text="Associated work order"
    )
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.PROTECT,
        related_name='releases',
        help_text="Bit being released"
    )

    # Release details
    status = models.CharField(
        max_length=20,
        choices=ReleaseStatus.choices,
        default=ReleaseStatus.DRAFT,
        db_index=True
    )
    planned_release_date = models.DateField(
        help_text="Planned dispatch date"
    )
    actual_release_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Actual dispatch date/time"
    )

    # Personnel
    prepared_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='prepared_releases',
        help_text="Employee who prepared the release"
    )
    qc_approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='qc_approved_releases',
        help_text="QC final approval"
    )
    qc_approval_date = models.DateTimeField(blank=True, null=True)

    # Customer/delivery info
    customer_name = models.CharField(max_length=200)
    delivery_address = models.TextField(
        help_text="Full delivery address"
    )
    customer_contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Customer contact person"
    )
    customer_contact_phone = models.CharField(max_length=20, blank=True)

    # Shipping
    transport_company = models.CharField(
        max_length=200,
        blank=True,
        help_text="Shipping company"
    )
    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Shipment tracking number"
    )
    awb_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Air Waybill number (if applicable)"
    )

    # Documentation
    delivery_note_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Delivery note number"
    )
    invoice_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Invoice number"
    )
    certificate_numbers = models.TextField(
        blank=True,
        help_text="Quality certificates, test reports, etc."
    )

    # Delivery confirmation
    delivered_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Actual delivery date"
    )
    received_by_customer = models.CharField(
        max_length=100,
        blank=True,
        help_text="Name of person who received at customer site"
    )
    customer_signature = models.CharField(
        max_length=100,
        blank=True,
        help_text="Signature reference or file path"
    )

    # Package details
    packaging_type = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., Wooden crate, cardboard box, etc."
    )
    number_of_packages = models.PositiveIntegerField(
        default=1,
        help_text="Number of packages/parcels"
    )
    total_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Total weight in kg"
    )

    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-planned_release_date', '-created_at']
        indexes = [
            models.Index(fields=['status', 'planned_release_date']),
            models.Index(fields=['work_order', 'status']),
            models.Index(fields=['customer_name']),
        ]
        verbose_name = 'Bit Release'
        verbose_name_plural = 'Bit Releases'

    def __str__(self):
        return f"{self.release_number} - {self.customer_name} ({self.get_status_display()})"


class BitLocationHistory(models.Model):
    """
    Track bit location changes throughout lifecycle
    Audit trail of where bit has been
    """
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.CASCADE,
        related_name='location_history'
    )
    location_status = models.CharField(
        max_length=30,
        choices=BitLocationStatus.choices,
        db_index=True
    )
    changed_at = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )
    changed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='location_changes'
    )

    # References to related transactions
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    receive_transaction = models.ForeignKey(
        BitReceive,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    release_transaction = models.ForeignKey(
        BitRelease,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    physical_location = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., 'Warehouse A, Shelf 5' or 'Finishing Dept, Station 3'"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
        indexes = [
            models.Index(fields=['bit_instance', '-changed_at']),
            models.Index(fields=['location_status', 'changed_at']),
        ]
        verbose_name = 'Bit Location History'
        verbose_name_plural = 'Bit Location Histories'

    def __str__(self):
        return f"{self.bit_instance.serial_number} - {self.get_location_status_display()} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"


# ============================================================================
# PROCESS TIME ANALYTICS & KPIs
# ============================================================================

class ProcessTimeMetric(models.Model):
    """
    Track actual process execution times for analytics and planning
    Calculates averages by bit size, type, and features
    """
    job_route_step = models.OneToOneField(
        JobRouteStep,
        on_delete=models.CASCADE,
        related_name='time_metric'
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='time_metrics'
    )
    process_code = models.CharField(max_length=100, db_index=True)
    
    # Bit characteristics for grouping
    bit_type = models.CharField(
        max_length=20,
        choices=BitType.choices
    )
    body_material = models.CharField(
        max_length=20,
        choices=BodyMaterial.choices,
        blank=True
    )
    bit_size_inch = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        help_text="Bit diameter for grouping metrics"
    )
    blade_count = models.PositiveIntegerField(blank=True, null=True)
    
    # Time measurements
    setup_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Time to setup for process"
    )
    processing_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Actual processing time"
    )
    wait_time_before_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Waiting time before process started"
    )
    total_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Total time from arrival to completion"
    )
    
    # Performance indicators
    operator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='process_metrics'
    )
    workstation = models.CharField(max_length=100, blank=True)
    department = models.CharField(
        max_length=30,
        choices=Department.choices
    )
    
    # Delay tracking
    delay_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reason for delays if any"
    )
    had_issues = models.BooleanField(
        default=False,
        help_text="Were there any issues during process?"
    )
    
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']
        indexes = [
            models.Index(fields=['process_code', 'bit_type', 'bit_size_inch']),
            models.Index(fields=['department', 'completed_at']),
            models.Index(fields=['operator', 'completed_at']),
        ]
    
    def __str__(self):
        return f"{self.process_code} - {self.bit_type} {self.bit_size_inch}\" - {self.processing_time_minutes}min"


class ProcessAverageTime(models.Model):
    """
    Aggregated average times for processes
    Updated periodically for planning purposes
    """
    process_code = models.CharField(max_length=100, db_index=True)
    bit_type = models.CharField(
        max_length=20,
        choices=BitType.choices
    )
    body_material = models.CharField(
        max_length=20,
        choices=BodyMaterial.choices,
        blank=True
    )
    bit_size_inch = models.DecimalField(
        max_digits=5,
        decimal_places=3
    )
    
    # Averages
    avg_setup_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    avg_processing_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    avg_wait_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    avg_total_time_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2
    )
    
    # Standard deviation for variability
    std_dev_processing_time = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    
    # Sample info
    sample_count = models.PositiveIntegerField(
        help_text="Number of samples in average"
    )
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['process_code', 'bit_type', 'body_material', 'bit_size_inch']]
        ordering = ['process_code', 'bit_type', 'bit_size_inch']
        indexes = [
            models.Index(fields=['process_code', 'bit_type']),
        ]
    
    def __str__(self):
        return f"{self.process_code} - {self.bit_type} {self.bit_size_inch}\" - Avg: {self.avg_processing_time_minutes}min"


class DepartmentKPI(models.Model):
    """
    Daily/Weekly KPIs for departments
    Track efficiency, throughput, delays
    """
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        db_index=True
    )
    date = models.DateField(db_index=True)
    shift = models.CharField(
        max_length=20,
        choices=[
            ('DAY', 'Day Shift'),
            ('NIGHT', 'Night Shift'),
            ('FULL_DAY', 'Full Day')
        ],
        default='FULL_DAY'
    )
    
    # Throughput
    jobs_completed = models.PositiveIntegerField(default=0)
    jobs_started = models.PositiveIntegerField(default=0)
    jobs_in_progress = models.PositiveIntegerField(default=0)
    
    # Time metrics
    total_processing_time_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    total_wait_time_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    total_downtime_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Equipment downtime"
    )
    
    # Efficiency
    efficiency_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Processing time / (Processing + Wait + Downtime)"
    )
    
    # Quality
    quality_holds_count = models.PositiveIntegerField(default=0)
    ncr_count = models.PositiveIntegerField(default=0)
    
    # Delays
    avg_delay_minutes = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )
    top_delay_reason = models.CharField(
        max_length=200,
        blank=True,
        help_text="Most common delay reason"
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['department', 'date', 'shift']]
        ordering = ['-date', 'department']
        indexes = [
            models.Index(fields=['department', '-date']),
        ]
    
    def __str__(self):
        return f"{self.get_department_display()} - {self.date} - Eff: {self.efficiency_percentage}%"


# ============================================================================
# MAINTENANCE & EQUIPMENT
# ============================================================================

class Equipment(models.Model):
    """
    Production equipment/machines
    """
    equipment_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique equipment ID (e.g., INFIL-01, LATHE-03)"
    )
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(
        max_length=100,
        help_text="e.g., Infiltration Furnace, CNC Lathe, Welding Station"
    )
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        db_index=True
    )
    location = models.CharField(
        max_length=200,
        help_text="Physical location in facility"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('OPERATIONAL', 'Operational'),
            ('MAINTENANCE', 'Under Maintenance'),
            ('BREAKDOWN', 'Broken Down'),
            ('IDLE', 'Idle'),
            ('DECOMMISSIONED', 'Decommissioned')
        ],
        default='OPERATIONAL',
        db_index=True
    )
    
    # Specifications
    manufacturer = models.CharField(max_length=200, blank=True)
    model_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    installation_date = models.DateField(blank=True, null=True)
    
    # Maintenance
    last_maintenance_date = models.DateField(blank=True, null=True)
    next_maintenance_date = models.DateField(
        blank=True,
        null=True,
        help_text="Scheduled preventive maintenance"
    )
    maintenance_interval_days = models.PositiveIntegerField(
        default=90,
        help_text="Days between preventive maintenance"
    )
    
    # Usage tracking
    total_operating_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['department', 'equipment_code']
        indexes = [
            models.Index(fields=['department', 'status']),
        ]
    
    def __str__(self):
        return f"{self.equipment_code} - {self.name} ({self.get_status_display()})"
    
    def is_maintenance_due(self):
        """Check if maintenance is overdue"""
        if not self.next_maintenance_date:
            return False
        from django.utils import timezone
        return self.next_maintenance_date <= timezone.now().date()


class MaintenanceRequest(models.Model):
    """
    Equipment maintenance requests and work orders
    """
    request_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique request number (e.g., MAINT-2025-001)"
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    request_type = models.CharField(
        max_length=20,
        choices=[
            ('BREAKDOWN', 'Breakdown/Emergency'),
            ('PREVENTIVE', 'Preventive Maintenance'),
            ('CALIBRATION', 'Calibration'),
            ('UPGRADE', 'Upgrade/Modification'),
            ('INSPECTION', 'Inspection')
        ],
        db_index=True
    )
    priority = models.CharField(
        max_length=20,
        choices=[
            ('CRITICAL', 'Critical - Production Stopped'),
            ('HIGH', 'High - Affecting Performance'),
            ('MEDIUM', 'Medium - Schedule Soon'),
            ('LOW', 'Low - Routine')
        ],
        default='MEDIUM',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('SUBMITTED', 'Submitted'),
            ('APPROVED', 'Approved'),
            ('IN_PROGRESS', 'In Progress'),
            ('WAITING_PARTS', 'Waiting for Parts'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='SUBMITTED',
        db_index=True
    )
    
    # Request details
    reported_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='maintenance_reports',
        help_text="Employee who reported the issue"
    )
    reported_by_name = models.CharField(max_length=100, blank=True)
    reported_at = models.DateTimeField(default=timezone.now)
    
    problem_description = models.TextField(
        help_text="Detailed description of the problem"
    )
    impact_on_production = models.TextField(
        blank=True,
        help_text="How this affects production"
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='assigned_maintenance',
        help_text="Maintenance technician assigned"
    )
    assigned_at = models.DateTimeField(blank=True, null=True)
    
    # Work performed
    work_started_at = models.DateTimeField(blank=True, null=True)
    work_completed_at = models.DateTimeField(blank=True, null=True)
    work_performed = models.TextField(
        blank=True,
        help_text="Description of work done"
    )
    parts_used = models.TextField(
        blank=True,
        help_text="Parts and materials used"
    )
    
    # Costs
    labor_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0
    )
    parts_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    
    # Downtime tracking
    downtime_start = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When equipment became unavailable"
    )
    downtime_end = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When equipment returned to service"
    )
    downtime_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Total downtime in hours"
    )
    
    # Jobs affected
    affected_job_cards = models.ManyToManyField(
        JobCard,
        blank=True,
        related_name='affected_by_maintenance',
        help_text="Job cards delayed by this maintenance"
    )
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['equipment', 'status']),
            models.Index(fields=['-reported_at']),
        ]
    
    def __str__(self):
        return f"{self.request_number} - {self.equipment.equipment_code} ({self.get_status_display()})"
    
    def calculate_downtime(self):
        """Calculate downtime in hours"""
        if self.downtime_start and self.downtime_end:
            delta = self.downtime_end - self.downtime_start
            return delta.total_seconds() / 3600
        return 0


# ============================================================================
# PROCESS VALIDATION & CORRECTION
# ============================================================================

class CorrectionRequestStatus(models.TextChoices):
    """Status of process correction requests"""
    PENDING = 'PENDING', 'Pending Supervisor Review'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'
    COMPLETED = 'COMPLETED', 'Correction Completed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class ProcessExecutionLog(models.Model):
    """
    Complete audit trail of all process executions
    Tracks every time an operator scans a QR code and starts/completes a process
    """
    log_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique execution log number"
    )

    # What was scanned
    job_route_step = models.ForeignKey(
        JobRouteStep,
        on_delete=models.CASCADE,
        related_name='execution_logs'
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='execution_logs'
    )
    process_code = models.CharField(max_length=100)

    # Who did it
    operator = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='process_executions'
    )
    operator_name = models.CharField(max_length=100, blank=True)

    # When
    scanned_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Validation results
    was_valid_sequence = models.BooleanField(
        default=True,
        help_text="Was this the correct next step in sequence?"
    )
    expected_process_code = models.CharField(
        max_length=100,
        blank=True,
        help_text="What process code was expected (if not valid)"
    )
    validation_message = models.TextField(
        blank=True,
        help_text="Validation result message"
    )

    # Execution details
    workstation = models.CharField(max_length=100, blank=True)
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        blank=True
    )
    notes = models.TextField(blank=True)

    # Correction tracking
    was_corrected = models.BooleanField(
        default=False,
        help_text="Was this execution later corrected/reversed?"
    )
    correction_request = models.ForeignKey(
        'ProcessCorrectionRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='corrected_executions'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']
        indexes = [
            models.Index(fields=['job_card', '-scanned_at']),
            models.Index(fields=['operator', '-scanned_at']),
            models.Index(fields=['was_valid_sequence']),
        ]
        verbose_name = 'Process Execution Log'
        verbose_name_plural = 'Process Execution Logs'

    def __str__(self):
        status = "✓ Valid" if self.was_valid_sequence else "✗ Invalid"
        return f"{self.log_number} - {self.process_code} ({status})"


class ProcessCorrectionRequest(models.Model):
    """
    Operator request to correct or reverse a wrongly executed process
    Requires supervisor approval
    """
    request_number = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique correction request number"
    )

    # What needs correction
    job_route_step = models.ForeignKey(
        JobRouteStep,
        on_delete=models.CASCADE,
        related_name='correction_requests'
    )
    job_card = models.ForeignKey(
        JobCard,
        on_delete=models.CASCADE,
        related_name='correction_requests'
    )
    execution_log = models.ForeignKey(
        ProcessExecutionLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='correction_requests',
        help_text="The execution log entry being corrected"
    )

    # Request details
    requested_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_correction_requests'
    )
    requested_by_name = models.CharField(max_length=100, blank=True)
    requested_at = models.DateTimeField(default=timezone.now)

    correction_type = models.CharField(
        max_length=30,
        choices=[
            ('REVERSE_STEP', 'Reverse Step - Mark as Not Done'),
            ('CHANGE_OPERATOR', 'Change Operator Assignment'),
            ('ADJUST_TIMES', 'Adjust Recorded Times'),
            ('CANCEL_EXECUTION', 'Cancel Wrong Execution'),
        ],
        default='REVERSE_STEP'
    )

    reason = models.TextField(
        help_text="Why does this need to be corrected?"
    )
    impact_description = models.TextField(
        blank=True,
        help_text="What is the impact of this mistake?"
    )

    # Approval workflow
    status = models.CharField(
        max_length=20,
        choices=CorrectionRequestStatus.choices,
        default=CorrectionRequestStatus.PENDING,
        db_index=True
    )

    supervisor_reviewed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_correction_requests',
        help_text="Supervisor who reviewed this request"
    )
    supervisor_reviewed_at = models.DateTimeField(blank=True, null=True)
    supervisor_decision_notes = models.TextField(
        blank=True,
        help_text="Supervisor's comments on approval/rejection"
    )

    # Execution of correction
    corrected_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When the correction was actually performed"
    )
    corrected_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_corrections',
        help_text="Who performed the correction"
    )
    correction_notes = models.TextField(
        blank=True,
        help_text="Notes about what was done to correct"
    )

    # Original state (for audit trail)
    original_step_status = models.CharField(
        max_length=20,
        blank=True,
        help_text="Original status of the route step before correction"
    )
    original_operator_name = models.CharField(
        max_length=100,
        blank=True
    )

    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
        help_text="How urgent is this correction?"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['status', '-requested_at']),
            models.Index(fields=['job_card', 'status']),
            models.Index(fields=['requested_by', '-requested_at']),
        ]
        verbose_name = 'Process Correction Request'
        verbose_name_plural = 'Process Correction Requests'

    def __str__(self):
        return f"{self.request_number} - {self.job_card.jobcard_code} ({self.get_status_display()})"

    def approve(self, supervisor, notes=""):
        """Approve the correction request"""
        self.status = CorrectionRequestStatus.APPROVED
        self.supervisor_reviewed_by = supervisor
        self.supervisor_reviewed_at = timezone.now()
        self.supervisor_decision_notes = notes
        self.save()

    def reject(self, supervisor, notes=""):
        """Reject the correction request"""
        self.status = CorrectionRequestStatus.REJECTED
        self.supervisor_reviewed_by = supervisor
        self.supervisor_reviewed_at = timezone.now()
        self.supervisor_decision_notes = notes
        self.save()

    def execute_correction(self, performed_by, notes=""):
        """Execute the approved correction"""
        if self.status != CorrectionRequestStatus.APPROVED:
            raise ValueError("Can only execute approved correction requests")

        # Perform the correction based on type
        if self.correction_type == 'REVERSE_STEP':
            # Mark the step back to PENDING
            self.job_route_step.status = RouteStepStatus.PENDING
            self.job_route_step.actual_start = None
            self.job_route_step.actual_end = None
            self.job_route_step.actual_operator = None
            self.job_route_step.save()

            # Mark execution log as corrected
            if self.execution_log:
                self.execution_log.was_corrected = True
                self.execution_log.correction_request = self
                self.execution_log.save()

        # Mark correction as completed
        self.status = CorrectionRequestStatus.COMPLETED
        self.corrected_at = timezone.now()
        self.corrected_by = performed_by
        self.correction_notes = notes
        self.save()


# ============================================================================
# BILL OF MATERIALS (BOM) & REPAIR HISTORY
# ============================================================================

class BOMItem(models.Model):
    """
    Bill of Materials for bit designs
    Tracks materials, cutters, and components needed
    """
    design_revision = models.ForeignKey(
        BitDesignRevision,
        on_delete=models.CASCADE,
        related_name='bom_items',
        help_text="Design this BOM applies to"
    )
    item_type = models.CharField(
        max_length=50,
        choices=[
            ('CUTTER', 'PDC Cutter'),
            ('NOZZLE', 'Nozzle'),
            ('BEARING', 'Bearing'),
            ('SEAL', 'Seal'),
            ('HARDFACING', 'Hardfacing Material'),
            ('POWDER', 'Matrix Powder'),
            ('BINDER', 'Binder/Infiltrant'),
            ('THREAD_COMPOUND', 'Thread Compound'),
            ('OTHER', 'Other Component'),
        ],
        db_index=True
    )
    part_number = models.CharField(
        max_length=100,
        help_text="Manufacturer part number"
    )
    description = models.TextField()
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Quantity required per bit"
    )
    unit = models.CharField(
        max_length=20,
        default='EA',
        help_text="Unit of measure (EA, LB, KG, etc.)"
    )
    manufacturer = models.CharField(max_length=200, blank=True)
    grade = models.CharField(
        max_length=100,
        blank=True,
        help_text="Material grade or specification"
    )
    is_critical = models.BooleanField(
        default=False,
        help_text="Critical component requiring special tracking"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['item_type', 'part_number']
        indexes = [
            models.Index(fields=['design_revision', 'item_type']),
            models.Index(fields=['part_number']),
        ]

    def __str__(self):
        return f"{self.part_number} - {self.description} ({self.quantity} {self.unit})"


class ActualBOM(models.Model):
    """
    Actual materials used for a specific work order
    Tracks what was actually used vs. what was planned
    """
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='actual_bom',
        help_text="Work order this BOM applies to"
    )
    bom_item = models.ForeignKey(
        BOMItem,
        on_delete=models.PROTECT,
        related_name='actual_usage',
        help_text="Reference BOM item"
    )
    planned_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Planned quantity from BOM"
    )
    actual_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        blank=True,
        null=True,
        help_text="Actual quantity used"
    )
    lot_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Lot/batch number of material used"
    )
    serial_numbers = models.TextField(
        blank=True,
        help_text="Serial numbers of critical components (one per line)"
    )
    variance_notes = models.TextField(
        blank=True,
        help_text="Notes on quantity variance or substitutions"
    )
    recorded_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='bom_records'
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['work_order', 'bom_item']
        indexes = [
            models.Index(fields=['work_order', 'bom_item']),
        ]

    def __str__(self):
        return f"{self.work_order.wo_number} - {self.bom_item.part_number}"

    def get_variance(self):
        """Calculate variance between planned and actual"""
        if self.actual_quantity is not None:
            return self.actual_quantity - self.planned_quantity
        return None


class RepairHistory(models.Model):
    """
    Detailed repair history for each repair cycle
    Tracks what was done, replaced, and observed
    """
    bit_instance = models.ForeignKey(
        BitInstance,
        on_delete=models.CASCADE,
        related_name='repair_history',
        help_text="Bit that was repaired"
    )
    work_order = models.OneToOneField(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='repair_record',
        help_text="Repair work order"
    )
    repair_index = models.PositiveIntegerField(
        help_text="Repair number (1=R1, 2=R2, etc.)"
    )
    evaluation_summary = models.ForeignKey(
        EvaluationSummary,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='repair_from_eval',
        help_text="Evaluation that triggered this repair"
    )

    # What was observed
    hours_on_bit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Hours bit was in use"
    )
    footage_drilled = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Footage drilled before return"
    )
    damage_description = models.TextField(
        blank=True,
        help_text="Description of damage observed"
    )

    # What was done
    cutters_replaced = models.PositiveIntegerField(
        default=0,
        help_text="Number of PDC cutters replaced"
    )
    nozzles_replaced = models.PositiveIntegerField(
        default=0,
        help_text="Number of nozzles replaced"
    )
    hardfacing_applied = models.BooleanField(
        default=False,
        help_text="Was hardfacing reapplied"
    )
    threads_repaired = models.BooleanField(
        default=False,
        help_text="Were threads repaired/re-cut"
    )
    gauge_repaired = models.BooleanField(
        default=False,
        help_text="Was gauge repaired/rebuilt"
    )
    balance_check = models.BooleanField(
        default=False,
        help_text="Was bit re-balanced"
    )

    # Repair route used
    route_template_used = models.ForeignKey(
        RouteTemplate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='repair_usage',
        help_text="Route template used for this repair"
    )

    # Reference to previous repairs
    previous_repair = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='subsequent_repairs',
        help_text="Previous repair in the chain"
    )

    # Completion info
    repair_completed_date = models.DateField(blank=True, null=True)
    repair_notes = models.TextField(
        blank=True,
        help_text="General notes about this repair cycle"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['bit_instance', 'repair_index']
        verbose_name_plural = 'Repair histories'
        indexes = [
            models.Index(fields=['bit_instance', 'repair_index']),
            models.Index(fields=['work_order']),
        ]
        unique_together = [['bit_instance', 'repair_index']]

    def __str__(self):
        return f"{self.bit_instance.serial_number}-R{self.repair_index} (WO: {self.work_order.wo_number})"

    def get_total_cost_estimate(self):
        """Estimate total repair cost based on components replaced"""
        # This would integrate with costing system
        pass


class RepairDecision(models.Model):
    """
    Automated repair route decision based on evaluation
    Helps determine which processes are needed
    """
    evaluation_summary = models.OneToOneField(
        EvaluationSummary,
        on_delete=models.CASCADE,
        related_name='repair_decision',
        help_text="Evaluation this decision is based on"
    )
    recommended_route = models.ForeignKey(
        RouteTemplate,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='recommended_for',
        help_text="Recommended route template"
    )

    # Required processes based on evaluation
    needs_cutter_replacement = models.BooleanField(default=False)
    needs_nozzle_replacement = models.BooleanField(default=False)
    needs_hardfacing = models.BooleanField(default=False)
    needs_thread_repair = models.BooleanField(default=False)
    needs_gauge_repair = models.BooleanField(default=False)
    needs_balance = models.BooleanField(default=False)
    needs_ndt = models.BooleanField(default=False)

    # Estimated resources
    estimated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text="Estimated repair hours"
    )
    estimated_cutter_count = models.PositiveIntegerField(
        default=0,
        help_text="Estimated cutters to replace"
    )

    decision_notes = models.TextField(
        blank=True,
        help_text="Reasoning for route selection"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='repair_decisions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Repair Decision for {self.evaluation_summary.job_card.jobcard_code}"

    def generate_route_recommendation(self):
        """
        Intelligently recommend a route template based on required processes
        """
        # This would query RouteTemplate and match based on required processes
        # For now, return a simple recommendation
        if self.needs_cutter_replacement or self.needs_gauge_repair:
            # Heavy repair
            return "REPAIR-HEAVY"
        elif self.needs_hardfacing or self.needs_thread_repair:
            # Medium repair
            return "REPAIR-MEDIUM"
        else:
            # Light repair
            return "REPAIR-LIGHT"


# ============================================================================
# CUTTER LAYOUT MANAGEMENT
# ============================================================================

class CutterZone(models.TextChoices):
    """Zones on PDC bit face"""
    CONE = 'CONE', 'Cone (Center)'
    SHOULDER = 'SHOULDER', 'Shoulder (Middle)'
    GAUGE = 'GAUGE', 'Gauge (Outer)'
    NOSE = 'NOSE', 'Nose (Transition)'


class CutterType(models.TextChoices):
    """PDC cutter types and profiles"""
    STANDARD_ROUND = 'STANDARD_ROUND', 'Standard Round PDC'
    CONICAL = 'CONICAL', 'Conical PDC'
    RIDGE = 'RIDGE', 'Ridge PDC'
    STINGER = 'STINGER', 'Stinger PDC'
    AXE = 'AXE', 'Axe PDC'
    DOME = 'DOME', 'Dome PDC'


class CutterLayoutPosition(models.Model):
    """
    Defines each cutter position on a bit design
    Maps the cutter grid: blade number, row number, position
    """
    design_revision = models.ForeignKey(
        BitDesignRevision,
        on_delete=models.CASCADE,
        related_name='cutter_positions',
        help_text="Design this layout applies to"
    )

    # Position identification
    blade_number = models.PositiveIntegerField(
        help_text="Blade number (1-7 typically)"
    )
    row_number = models.PositiveIntegerField(
        help_text="Row number from center (1=center, increasing outward)"
    )
    position_in_row = models.PositiveIntegerField(
        default=1,
        help_text="Position within the row (for multiple cutters per row)"
    )

    # Zone classification
    zone = models.CharField(
        max_length=20,
        choices=CutterZone.choices,
        help_text="Functional zone on bit face"
    )

    # Cutter specification for this position
    cutter_size_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Cutter diameter in mm (e.g., 13.00, 16.00, 19.00)"
    )
    cutter_type = models.CharField(
        max_length=30,
        choices=CutterType.choices,
        default=CutterType.STANDARD_ROUND,
        help_text="Cutter profile type"
    )

    # Orientation and geometry
    back_rake_angle = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Back rake angle in degrees (0-30°, negative for aggressive)"
    )
    side_rake_angle = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Side rake angle in degrees"
    )
    exposure_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Cutter exposure above blade in mm"
    )

    # Position coordinates (for visualization)
    radial_position_mm = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Distance from bit center in mm"
    )
    angular_position_degrees = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Angular position on blade (0-360°)"
    )

    # BOM linkage
    bom_item = models.ForeignKey(
        BOMItem,
        on_delete=models.PROTECT,
        related_name='cutter_positions',
        help_text="BOM item for this cutter specification"
    )

    # Design intent notes
    is_critical_for_performance = models.BooleanField(
        default=False,
        help_text="Critical position (cannot substitute)"
    )
    substitution_allowed = models.BooleanField(
        default=True,
        help_text="Can this cutter be substituted with similar spec?"
    )
    notes = models.TextField(
        blank=True,
        help_text="Special notes for this position"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['blade_number', 'row_number', 'position_in_row']
        indexes = [
            models.Index(fields=['design_revision', 'blade_number']),
            models.Index(fields=['zone', 'cutter_size_mm']),
        ]
        unique_together = [['design_revision', 'blade_number', 'row_number', 'position_in_row']]
        verbose_name_plural = 'Cutter layout positions'

    def __str__(self):
        return f"B{self.blade_number}-R{self.row_number}-P{self.position_in_row}: {self.cutter_size_mm}mm {self.get_cutter_type_display()}"

    def get_position_code(self):
        """Generate unique position code (e.g., B1-R3-P1)"""
        return f"B{self.blade_number}-R{self.row_number}-P{self.position_in_row}"


class ActualCutterInstallation(models.Model):
    """
    Tracks actual cutters installed in each position
    Records as-built or as-repaired cutter layout
    """
    work_order = models.ForeignKey(
        WorkOrder,
        on_delete=models.CASCADE,
        related_name='cutter_installations',
        help_text="Work order (build or repair) this installation belongs to"
    )
    layout_position = models.ForeignKey(
        CutterLayoutPosition,
        on_delete=models.PROTECT,
        related_name='actual_installations',
        help_text="Design position for this cutter"
    )

    # Installation details
    installation_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date cutter was installed"
    )
    installed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='cutter_installations',
        help_text="Technician who installed this cutter"
    )

    # Actual cutter installed (may differ from design)
    actual_cutter_size_mm = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Actual cutter size installed"
    )
    actual_cutter_type = models.CharField(
        max_length=30,
        choices=CutterType.choices,
        help_text="Actual cutter type installed"
    )
    actual_bom_item = models.ForeignKey(
        BOMItem,
        on_delete=models.PROTECT,
        related_name='actual_installations',
        help_text="Actual BOM item used"
    )

    # Traceability
    cutter_serial_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Individual cutter serial number (if tracked)"
    )
    cutter_lot_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Lot/batch number of cutter"
    )
    manufacturer = models.CharField(
        max_length=200,
        blank=True,
        help_text="Cutter manufacturer"
    )

    # Deviation tracking
    is_substitution = models.BooleanField(
        default=False,
        help_text="True if this differs from design specification"
    )
    substitution_reason = models.TextField(
        blank=True,
        help_text="Reason for substitution (material shortage, engineering change, etc.)"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_cutter_substitutions',
        help_text="Engineer who approved substitution"
    )

    # Installation quality
    braze_quality_check = models.CharField(
        max_length=20,
        choices=[
            ('PASS', 'Pass'),
            ('FAIL', 'Fail'),
            ('REWORK', 'Rework'),
            ('NOT_CHECKED', 'Not Checked'),
        ],
        default='NOT_CHECKED',
        help_text="Braze quality inspection result"
    )
    leak_test_result = models.CharField(
        max_length=20,
        choices=[
            ('PASS', 'Pass'),
            ('FAIL', 'Fail'),
            ('NOT_TESTED', 'Not Tested'),
        ],
        default='NOT_TESTED',
        help_text="Leak test result"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('INSTALLED', 'Installed'),
            ('DAMAGED', 'Damaged'),
            ('REPLACED', 'Replaced'),
            ('REMOVED', 'Removed'),
        ],
        default='INSTALLED',
        help_text="Current status of this cutter"
    )
    removal_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date cutter was removed (during repair)"
    )
    removal_reason = models.TextField(
        blank=True,
        help_text="Reason for removal"
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            'work_order',
            'layout_position__blade_number',
            'layout_position__row_number'
        ]
        indexes = [
            models.Index(fields=['work_order', 'status']),
            models.Index(fields=['layout_position', 'status']),
        ]

    def __str__(self):
        position = self.layout_position.get_position_code()
        return f"{self.work_order.wo_number} - {position}: {self.actual_cutter_size_mm}mm"

    def is_per_design(self):
        """Check if installed cutter matches design specification"""
        return (
            self.actual_cutter_size_mm == self.layout_position.cutter_size_mm and
            self.actual_cutter_type == self.layout_position.cutter_type and
            not self.is_substitution
        )

    def get_deviation_description(self):
        """Describe how installation deviates from design"""
        if self.is_per_design():
            return "Per design"

        deviations = []
        if self.actual_cutter_size_mm != self.layout_position.cutter_size_mm:
            deviations.append(
                f"Size: {self.layout_position.cutter_size_mm}mm → {self.actual_cutter_size_mm}mm"
            )
        if self.actual_cutter_type != self.layout_position.cutter_type:
            deviations.append(
                f"Type: {self.layout_position.get_cutter_type_display()} → {self.get_actual_cutter_type_display()}"
            )

        return "; ".join(deviations)


class CutterLayoutRevision(models.Model):
    """
    Tracks changes to cutter layouts over time
    Documents engineering changes and field feedback
    """
    design_revision = models.ForeignKey(
        BitDesignRevision,
        on_delete=models.CASCADE,
        related_name='layout_revisions',
        help_text="Design this layout revision applies to"
    )
    revision_number = models.CharField(
        max_length=20,
        help_text="Layout revision number (e.g., LAY-001, LAY-002)"
    )
    revision_date = models.DateField(
        help_text="Date of layout revision"
    )

    # Change description
    change_description = models.TextField(
        help_text="Description of what changed in this revision"
    )
    reason_for_change = models.TextField(
        help_text="Why the change was made (field performance, cost reduction, etc.)"
    )

    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='approved_layout_revisions',
        help_text="Engineer who approved this revision"
    )
    approval_date = models.DateField(
        blank=True,
        null=True
    )

    # Effectivity
    effective_from_wo = models.CharField(
        max_length=50,
        blank=True,
        help_text="First work order to use this revision"
    )

    # Performance tracking
    field_performance_notes = models.TextField(
        blank=True,
        help_text="Field performance feedback for this layout"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-revision_date']
        unique_together = [['design_revision', 'revision_number']]

    def __str__(self):
        return f"{self.design_revision.mat_number} - {self.revision_number}"
