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
from django.core.validators import MinValueValidator
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
    Core bit design/blueprint (e.g., HD75WF)
    Represents the engineering design of a bit type
    """
    design_code = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Unique design code (e.g., HD75WF)"
    )
    bit_type = models.CharField(
        max_length=20,
        choices=BitType.choices,
        help_text="Type of bit: PDC or Roller Cone"
    )
    body_material = models.CharField(
        max_length=20,
        choices=BodyMaterial.choices,
        blank=True,
        null=True,
        help_text="Body material (relevant for PDC bits)"
    )
    size_inch = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        validators=[MinValueValidator(0)],
        help_text="Bit diameter in inches (e.g., 12.25)"
    )
    blade_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of blades (for PDC bits)"
    )
    nozzle_count = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text="Number of nozzles"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed design description"
    )
    active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Is this design currently active?"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['design_code']
        indexes = [
            models.Index(fields=['bit_type', 'active']),
            models.Index(fields=['size_inch']),
        ]

    def __str__(self):
        return f"{self.design_code} ({self.get_bit_type_display()}, {self.size_inch}\")"


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
    phone = models.CharField(max_length=20, blank=True)
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
