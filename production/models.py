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
