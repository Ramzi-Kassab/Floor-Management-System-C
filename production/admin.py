# -*- coding: utf-8 -*-
"""
Django Admin Configuration for Production Department
"""

from django.contrib import admin
from django.utils.html import format_html
from . import models


# ============================================================================
# BIT DESIGN & INSTANCES
# ============================================================================

@admin.register(models.BitDesign)
class BitDesignAdmin(admin.ModelAdmin):
    list_display = ['bit_type', 'size_inch', 'current_smi_name', 'hdbs_name', 'iadc_code',
                    'body_material', 'blade_count', 'active', 'created_at']
    list_filter = ['bit_type', 'body_material', 'connection_type', 'active', 'created_at']
    search_fields = ['design_code', 'current_smi_name', 'hdbs_name', 'iadc_code',
                     'description', 'remarks']
    date_hierarchy = 'created_at'
    list_per_page = 50

    # Field order as specified: Bit Cat, Size, SMI Name, HDBS, IADC, Body, Blades, etc.
    fieldsets = (
        ('Bit Category & Identification', {
            'fields': ('bit_type', 'size_inch', 'design_code', 'design_mat_number'),
            'description': 'Bit Category (FC/RC), basic identification, and Level-1 MAT'
        }),
        ('Design Names & Codes', {
            'fields': ('current_smi_name', 'hdbs_name', 'iadc_code'),
            'description': 'ARDT/SMI name, Halliburton name, and IADC code'
        }),
        ('Fixed Cutter (PDC) Specifications', {
            'fields': ('body_material', 'blade_count', 'cutter_size_category',
                      'gauge_length_inch'),
            'description': 'Auto-filled from design name if empty. Matrix/Steel, blade count (1st digit), cutter size (2nd digit)'
        }),
        ('Connection & Gauge Geometry', {
            'fields': ('connection_type', 'shank_diameter_inch', 'gauge_relief_thou',
                      'breaker_slot_width_inch', 'breaker_slot_height_inch'),
            'description': 'Connection details, shank diameter, gauge relief, and breaker slot dimensions'
        }),
        ('Hydraulics', {
            'fields': ('nozzle_count', 'port_count'),
            'description': 'Nozzles and ports'
        }),
        ('Description & Notes', {
            'fields': ('description', 'remarks'),
            'description': 'Description is auto-generated ({size}-{name}-{iadc}). Use Remarks for manual notes.'
        }),
        ('Status', {
            'fields': ('active',),
            'classes': ('collapse',)
        }),
    )

    def get_readonly_fields(self, request, obj=None):
        # Show description as readonly if it's auto-generated
        if obj and obj.description and not request.GET.get('force_edit_description'):
            return ['description']
        return []


@admin.register(models.BitDesignRevision)
class BitDesignRevisionAdmin(admin.ModelAdmin):
    list_display = ['mat_number', 'design', 'level', 'previous_level', 'upper_welded', 'effective_from', 'effective_to', 'active']
    list_filter = ['active', 'level', 'upper_welded', 'effective_from']
    search_fields = ['mat_number', 'design__design_code', 'remarks']
    date_hierarchy = 'effective_from'
    list_per_page = 50
    autocomplete_fields = ['design', 'previous_level']
    fieldsets = (
        ('Revision Information', {
            'fields': ('design', 'mat_number', 'level', 'previous_level', 'upper_welded')
        }),
        ('Effective Dates', {
            'fields': ('effective_from', 'effective_to', 'active')
        }),
        ('Notes', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.BitInstance)
class BitInstanceAdmin(admin.ModelAdmin):
    list_display = ['get_full_serial_display', 'design_revision', 'body_material',
                    'manufacturing_source', 'current_repair_index', 'status', 'created_at']
    list_filter = ['status', 'body_material', 'manufacturing_source', 'current_repair_index', 'created_at']
    search_fields = ['serial_number', 'design_revision__mat_number', 'design_revision__design__design_code']
    date_hierarchy = 'created_at'
    list_per_page = 50
    autocomplete_fields = ['design_revision', 'initial_build_wo']

    def get_full_serial_display(self, obj):
        return obj.get_full_serial()
    get_full_serial_display.short_description = 'Serial Number'

    fieldsets = (
        ('Bit Identity', {
            'fields': ('serial_number', 'design_revision')
        }),
        ('Manufacturing', {
            'fields': ('body_material', 'manufacturing_source', 'initial_build_wo')
        }),
        ('Status & Repair', {
            'fields': ('current_repair_index', 'status')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


# ============================================================================
# WORK ORDERS & JOB CARDS
# ============================================================================

@admin.register(models.WorkOrder)
class WorkOrderAdmin(admin.ModelAdmin):
    list_display = ['wo_number', 'order_type', 'customer_name', 'design_revision',
                    'priority', 'status', 'due_date', 'created_at']
    list_filter = ['order_type', 'status', 'priority', 'rent_or_sale_type', 'created_at']
    search_fields = ['wo_number', 'customer_name', 'rig', 'well', 'field', 'external_reference']
    date_hierarchy = 'created_at'
    list_per_page = 50
    autocomplete_fields = ['bit_instance', 'design_revision']

    fieldsets = (
        ('Work Order Information', {
            'fields': ('wo_number', 'order_type', 'priority', 'status')
        }),
        ('Bit Details', {
            'fields': ('bit_instance', 'design_revision')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'rig', 'well', 'field', 'rent_or_sale_type')
        }),
        ('Scheduling', {
            'fields': ('received_date', 'due_date')
        }),
        ('Additional Info', {
            'fields': ('remarks', 'external_reference')
        }),
    )


class JobRouteStepInline(admin.TabularInline):
    model = models.JobRouteStep
    extra = 0
    fields = ['sequence', 'process_code', 'department', 'status', 'operator_name']
    readonly_fields = ['sequence', 'process_code']


@admin.register(models.JobCard)
class JobCardAdmin(admin.ModelAdmin):
    list_display = ['jobcard_code', 'work_order', 'job_type', 'department',
                    'status', 'is_repair', 'created_at']
    list_filter = ['status', 'department', 'is_repair', 'job_type', 'created_at']
    search_fields = ['jobcard_code', 'work_order__wo_number', 'current_workstation']
    date_hierarchy = 'created_at'
    list_per_page = 50
    autocomplete_fields = ['work_order']
    inlines = [JobRouteStepInline]

    fieldsets = (
        ('Job Card Information', {
            'fields': ('jobcard_code', 'work_order', 'job_type', 'is_repair')
        }),
        ('Department & Location', {
            'fields': ('department', 'current_workstation')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Scheduling', {
            'fields': ('planned_start', 'planned_end', 'actual_start', 'actual_end')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


# ============================================================================
# ROUTING
# ============================================================================

class RouteStepTemplateInline(admin.TabularInline):
    model = models.RouteStepTemplate
    extra = 1
    fields = ['sequence', 'process_code', 'description', 'default_department',
              'estimated_duration_minutes', 'is_mandatory']


@admin.register(models.RouteTemplate)
class RouteTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'bit_type', 'body_material', 'for_order_type',
                    'department_focus', 'active']
    list_filter = ['bit_type', 'body_material', 'for_order_type', 'department_focus', 'active']
    search_fields = ['name', 'description']
    list_per_page = 50
    inlines = [RouteStepTemplateInline]

    fieldsets = (
        ('Route Information', {
            'fields': ('name', 'description')
        }),
        ('Applicability', {
            'fields': ('bit_type', 'body_material', 'for_order_type', 'department_focus')
        }),
        ('Status', {
            'fields': ('active',)
        }),
    )


@admin.register(models.RouteStepTemplate)
class RouteStepTemplateAdmin(admin.ModelAdmin):
    list_display = ['route', 'sequence', 'process_code', 'default_department',
                    'estimated_duration_minutes', 'is_mandatory']
    list_filter = ['default_department', 'is_mandatory', 'route']
    search_fields = ['process_code', 'description', 'route__name']
    list_per_page = 100
    autocomplete_fields = ['route']


@admin.register(models.JobRouteStep)
class JobRouteStepAdmin(admin.ModelAdmin):
    list_display = ['job_card', 'sequence', 'process_code', 'department',
                    'status', 'operator', 'actual_start']
    list_filter = ['status', 'department', 'created_at']
    search_fields = ['job_card__jobcard_code', 'process_code', 'operator_name']
    date_hierarchy = 'created_at'
    list_per_page = 100
    autocomplete_fields = ['job_card', 'template', 'operator']

    fieldsets = (
        ('Step Information', {
            'fields': ('job_card', 'template', 'sequence', 'process_code', 'description')
        }),
        ('Location & Operator', {
            'fields': ('department', 'workstation', 'operator', 'operator_name')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timing', {
            'fields': ('planned_start', 'planned_end', 'actual_start', 'actual_end')
        }),
        ('Notes', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.JobPause)
class JobPauseAdmin(admin.ModelAdmin):
    list_display = ['job_card', 'reason', 'start_time', 'end_time', 'get_duration']
    list_filter = ['reason', 'start_time']
    search_fields = ['job_card__jobcard_code', 'reason', 'notes']
    date_hierarchy = 'start_time'
    list_per_page = 100
    autocomplete_fields = ['job_card']

    def get_duration(self, obj):
        if obj.end_time:
            duration = (obj.end_time - obj.start_time).total_seconds() / 3600
            return f"{duration:.1f} hours"
        return "Ongoing"
    get_duration.short_description = 'Duration'


# ============================================================================
# INFILTRATION
# ============================================================================

class InfiltrationBatchItemInline(admin.TabularInline):
    model = models.InfiltrationBatchItem
    extra = 0
    fields = ['job_card', 'mold_id', 'powder_mix_code', 'status']
    autocomplete_fields = ['job_card']


@admin.register(models.InfiltrationBatch)
class InfiltrationBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_code', 'furnace_id', 'status', 'planned_start',
                    'actual_start', 'get_item_count']
    list_filter = ['status', 'furnace_id', 'planned_start']
    search_fields = ['batch_code', 'furnace_id', 'operator_name']
    date_hierarchy = 'planned_start'
    list_per_page = 50
    autocomplete_fields = ['operator']
    inlines = [InfiltrationBatchItemInline]

    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'

    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_code', 'furnace_id', 'status')
        }),
        ('Scheduling', {
            'fields': ('planned_start', 'planned_end', 'actual_start', 'actual_end')
        }),
        ('Operation', {
            'fields': ('operator', 'operator_name', 'temperature_profile')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(models.InfiltrationBatchItem)
class InfiltrationBatchItemAdmin(admin.ModelAdmin):
    list_display = ['batch', 'job_card', 'mold_id', 'powder_mix_code', 'status']
    list_filter = ['status', 'batch__furnace_id', 'created_at']
    search_fields = ['batch__batch_code', 'job_card__jobcard_code', 'mold_id', 'powder_mix_code']
    date_hierarchy = 'created_at'
    list_per_page = 100
    autocomplete_fields = ['batch', 'job_card']


# ============================================================================
# QC & EVALUATION
# ============================================================================

@admin.register(models.EvaluationSummary)
class EvaluationSummaryAdmin(admin.ModelAdmin):
    list_display = ['job_card', 'evaluation_date', 'evaluator_name',
                    'overall_condition', 'recommended_action']
    list_filter = ['overall_condition', 'recommended_action', 'evaluation_date']
    search_fields = ['job_card__jobcard_code', 'evaluator_name', 'remarks']
    date_hierarchy = 'evaluation_date'
    list_per_page = 50
    autocomplete_fields = ['job_card']

    fieldsets = (
        ('Evaluation Information', {
            'fields': ('job_card', 'evaluation_date', 'evaluator_name')
        }),
        ('Assessment', {
            'fields': ('overall_condition', 'recommended_action')
        }),
        ('Details', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.NDTResult)
class NDTResultAdmin(admin.ModelAdmin):
    list_display = ['job_card', 'method', 'result', 'inspector_name', 'performed_at']
    list_filter = ['method', 'result', 'performed_at']
    search_fields = ['job_card__jobcard_code', 'inspector_name', 'comments']
    date_hierarchy = 'performed_at'
    list_per_page = 100
    autocomplete_fields = ['job_card']

    fieldsets = (
        ('Test Information', {
            'fields': ('job_card', 'method', 'performed_at', 'inspector_name')
        }),
        ('Result', {
            'fields': ('result',)
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
    )


@admin.register(models.ThreadInspectionResult)
class ThreadInspectionResultAdmin(admin.ModelAdmin):
    list_display = ['job_card', 'connection_type', 'result', 'gauge_used',
                    'inspector_name', 'performed_at']
    list_filter = ['result', 'connection_type', 'performed_at']
    search_fields = ['job_card__jobcard_code', 'connection_type', 'inspector_name', 'gauge_used']
    date_hierarchy = 'performed_at'
    list_per_page = 100
    autocomplete_fields = ['job_card']

    fieldsets = (
        ('Inspection Information', {
            'fields': ('job_card', 'connection_type', 'performed_at', 'inspector_name')
        }),
        ('Test Details', {
            'fields': ('gauge_used', 'result')
        }),
        ('Comments', {
            'fields': ('comments',)
        }),
    )


# ============================================================================
# QR CODES
# ============================================================================

@admin.register(models.QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'get_target_display', 'created_at', 'expires_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['code', 'job_card__jobcard_code', 'notes']
    date_hierarchy = 'created_at'
    list_per_page = 100
    autocomplete_fields = ['job_card', 'route_step']
    readonly_fields = ['code']

    def get_target_display(self, obj):
        target = obj.get_target()
        if target:
            return str(target)
        return "No target"
    get_target_display.short_description = 'Target'

    fieldsets = (
        ('QR Code', {
            'fields': ('code',)
        }),
        ('Target', {
            'fields': ('job_card', 'route_step')
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


# Configure search fields for autocomplete
BitDesignAdmin.search_fields = ['design_code', 'description']
BitDesignRevisionAdmin.search_fields = ['mat_number', 'design__design_code']
WorkOrderAdmin.search_fields = ['wo_number', 'customer_name']
JobCardAdmin.search_fields = ['jobcard_code', 'work_order__wo_number']


# ============================================================================
# QUALITY MANAGEMENT & NCR
# ============================================================================

@admin.register(models.NonConformanceReport)
class NonConformanceReportAdmin(admin.ModelAdmin):
    list_display = ['ncr_number', 'severity', 'status', 'detected_at_process',
                    'detected_by', 'detected_date', 'disposition']
    list_filter = ['severity', 'status', 'disposition', 'detected_date']
    search_fields = ['ncr_number', 'description', 'detected_by', 'job_card__jobcard_code']
    date_hierarchy = 'detected_date'
    list_per_page = 50
    autocomplete_fields = ['job_card', 'work_order', 'bit_instance']
    
    fieldsets = (
        ('NCR Information', {
            'fields': ('ncr_number', 'severity', 'status')
        }),
        ('Detection', {
            'fields': ('detected_at_process', 'detected_by', 'detected_date',
                      'job_card', 'work_order', 'bit_instance')
        }),
        ('Description & Analysis', {
            'fields': ('description', 'root_cause', 'corrective_action', 'preventive_action')
        }),
        ('Disposition (MRB Decision)', {
            'fields': ('disposition', 'disposition_date', 'disposition_by', 'disposition_notes')
        }),
        ('Closure', {
            'fields': ('closed_date', 'closed_by')
        }),
        ('Cost Impact', {
            'fields': ('estimated_cost_impact',)
        }),
    )


@admin.register(models.ScrapRecord)
class ScrapRecordAdmin(admin.ModelAdmin):
    list_display = ['scrap_number', 'item_description', 'scrap_reason',
                    'quantity', 'total_cost', 'scrap_date', 'approved_by']
    list_filter = ['scrap_reason', 'scrap_date', 'unit']
    search_fields = ['scrap_number', 'item_description', 'approved_by',
                    'bit_instance__serial_number']
    date_hierarchy = 'scrap_date'
    list_per_page = 50
    autocomplete_fields = ['bit_instance', 'job_card', 'ncr']
    
    fieldsets = (
        ('Scrap Information', {
            'fields': ('scrap_number', 'scrap_reason', 'scrap_date')
        }),
        ('Item Details', {
            'fields': ('item_description', 'quantity', 'unit',
                      'bit_instance', 'job_card', 'ncr')
        }),
        ('Cost Tracking', {
            'fields': ('material_cost', 'labor_cost', 'total_cost')
        }),
        ('Approval', {
            'fields': ('approved_by', 'approval_date')
        }),
        ('Recovery/Salvage', {
            'fields': ('salvage_value', 'salvage_notes')
        }),
        ('Additional Notes', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.ReworkRecord)
class ReworkRecordAdmin(admin.ModelAdmin):
    list_display = ['rework_number', 'job_card', 'rework_reason', 'status',
                    'actual_start', 'actual_end', 'total_cost']
    list_filter = ['status', 'rework_reason', 'actual_start']
    search_fields = ['rework_number', 'job_card__jobcard_code', 'rework_description',
                    'assigned_to_name']
    date_hierarchy = 'actual_start'
    list_per_page = 50
    autocomplete_fields = ['job_card', 'ncr', 'assigned_to']
    
    fieldsets = (
        ('Rework Information', {
            'fields': ('rework_number', 'job_card', 'ncr', 'rework_reason', 'status')
        }),
        ('Description', {
            'fields': ('original_process', 'rework_description', 'rework_instructions')
        }),
        ('Scheduling', {
            'fields': ('planned_start', 'planned_end', 'actual_start', 'actual_end')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_to_name')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_date', 'verification_notes')
        }),
        ('Cost Tracking', {
            'fields': ('labor_hours', 'material_cost', 'total_cost')
        }),
        ('Additional Notes', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.ProductionHold)
class ProductionHoldAdmin(admin.ModelAdmin):
    list_display = ['hold_number', 'job_card', 'hold_reason', 'status',
                    'hold_start', 'hold_end', 'get_duration_display', 'cost_impact']
    list_filter = ['status', 'hold_reason', 'requires_approval', 'hold_start']
    search_fields = ['hold_number', 'job_card__jobcard_code', 'description',
                    'hold_initiated_by']
    date_hierarchy = 'hold_start'
    list_per_page = 50
    autocomplete_fields = ['job_card', 'work_order']
    
    def get_duration_display(self, obj):
        hours = obj.get_duration_hours()
        return f"{hours:.1f}h"
    get_duration_display.short_description = 'Duration'
    
    fieldsets = (
        ('Hold Information', {
            'fields': ('hold_number', 'job_card', 'work_order', 'status')
        }),
        ('Hold Details', {
            'fields': ('hold_reason', 'hold_initiated_by', 'hold_start', 'hold_end')
        }),
        ('Description & Resolution', {
            'fields': ('description', 'resolution')
        }),
        ('Approval (if required)', {
            'fields': ('requires_approval', 'approved_for_release_by', 'approval_date')
        }),
        ('Impact Assessment', {
            'fields': ('estimated_delay_hours', 'cost_impact')
        }),
        ('Additional Notes', {
            'fields': ('remarks',)
        }),
    )


# ============================================================================
# EMPLOYEE MANAGEMENT
# ============================================================================

@admin.register(models.Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_code', 'get_full_name', 'department', 'role', 'status', 'hire_date']
    list_filter = ['department', 'role', 'status']
    search_fields = ['employee_code', 'first_name', 'last_name', 'email']
    autocomplete_fields = ['user']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_code', 'user', 'first_name', 'last_name')
        }),
        ('Department & Role', {
            'fields': ('department', 'role', 'status')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email')
        }),
        ('Employment Details', {
            'fields': ('hire_date', 'skills')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


# ============================================================================
# BIT RECEIVING & RELEASE
# ============================================================================

@admin.register(models.BitReceive)
class BitReceiveAdmin(admin.ModelAdmin):
    list_display = ['receive_number', 'customer_name', 'received_date', 'inspection_status', 'received_by']
    list_filter = ['inspection_status', 'package_condition', 'received_date']
    search_fields = ['receive_number', 'customer_name', 'tracking_number']
    autocomplete_fields = ['work_order', 'bit_instance', 'received_by', 'inspected_by']
    date_hierarchy = 'received_date'

    fieldsets = (
        ('Receive Information', {
            'fields': ('receive_number', 'work_order', 'bit_instance', 'received_date')
        }),
        ('Received By', {
            'fields': ('received_by', 'received_by_name')
        }),
        ('Customer & Shipping', {
            'fields': ('customer_name', 'transport_company', 'tracking_number')
        }),
        ('Package Condition', {
            'fields': ('package_condition',)
        }),
        ('Inspection', {
            'fields': ('inspection_status', 'inspected_by', 'inspection_date', 'inspection_notes')
        }),
        ('Documentation', {
            'fields': ('customer_po', 'packing_slip', 'has_bit_record', 'photo_paths')
        }),
        ('Remarks', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.BitRelease)
class BitReleaseAdmin(admin.ModelAdmin):
    list_display = ['release_number', 'customer_name', 'status', 'planned_release_date', 'actual_release_date']
    list_filter = ['status', 'planned_release_date']
    search_fields = ['release_number', 'customer_name', 'tracking_number', 'invoice_number']
    autocomplete_fields = ['work_order', 'bit_instance', 'prepared_by', 'qc_approved_by']
    date_hierarchy = 'planned_release_date'

    fieldsets = (
        ('Release Information', {
            'fields': ('release_number', 'work_order', 'bit_instance', 'status')
        }),
        ('Dates', {
            'fields': ('planned_release_date', 'actual_release_date', 'delivered_date')
        }),
        ('Personnel', {
            'fields': ('prepared_by', 'qc_approved_by', 'qc_approval_date')
        }),
        ('Customer Information', {
            'fields': ('customer_name', 'delivery_address', 'customer_contact_name', 'customer_contact_phone')
        }),
        ('Shipping', {
            'fields': ('transport_company', 'tracking_number', 'awb_number')
        }),
        ('Package Details', {
            'fields': ('packaging_type', 'number_of_packages', 'total_weight_kg')
        }),
        ('Documentation', {
            'fields': ('delivery_note_number', 'invoice_number', 'certificate_numbers')
        }),
        ('Delivery Confirmation', {
            'fields': ('received_by_customer', 'customer_signature')
        }),
        ('Remarks', {
            'fields': ('remarks',)
        }),
    )


@admin.register(models.BitLocationHistory)
class BitLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ['bit_instance', 'location_status', 'changed_at', 'changed_by', 'physical_location']
    list_filter = ['location_status', 'changed_at']
    search_fields = ['bit_instance__serial_number', 'physical_location']
    autocomplete_fields = ['bit_instance', 'changed_by', 'work_order', 'job_card', 'receive_transaction', 'release_transaction']
    date_hierarchy = 'changed_at'
    readonly_fields = ['created_at']

    fieldsets = (
        ('Location Change', {
            'fields': ('bit_instance', 'location_status', 'changed_at', 'changed_by')
        }),
        ('Physical Location', {
            'fields': ('physical_location',)
        }),
        ('Related Transactions', {
            'fields': ('work_order', 'job_card', 'receive_transaction', 'release_transaction')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


# ============================================================================
# ANALYTICS & KPIs
# ============================================================================

@admin.register(models.ProcessTimeMetric)
class ProcessTimeMetricAdmin(admin.ModelAdmin):
    list_display = ['process_code', 'job_card', 'bit_type', 'bit_size_inch', 'processing_time_minutes', 'wait_time_before_minutes', 'operator', 'completed_at']
    list_filter = ['bit_type', 'body_material', 'department', 'had_issues']
    search_fields = ['process_code', 'job_card__jobcard_code']
    autocomplete_fields = ['job_route_step', 'job_card', 'operator']
    date_hierarchy = 'completed_at'
    readonly_fields = ['completed_at']


@admin.register(models.ProcessAverageTime)
class ProcessAverageTimeAdmin(admin.ModelAdmin):
    list_display = ['process_code', 'bit_type', 'bit_size_inch', 'avg_processing_time_minutes', 'avg_wait_time_minutes', 'sample_count', 'last_updated']
    list_filter = ['bit_type', 'body_material']
    search_fields = ['process_code']
    readonly_fields = ['last_updated']


@admin.register(models.DepartmentKPI)
class DepartmentKPIAdmin(admin.ModelAdmin):
    list_display = ['department', 'date', 'shift', 'efficiency_percentage', 'jobs_completed', 'total_downtime_hours', 'ncr_count']
    list_filter = ['department', 'shift', 'date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Period', {
            'fields': ('department', 'date', 'shift')
        }),
        ('Throughput', {
            'fields': ('jobs_completed', 'jobs_started', 'jobs_in_progress')
        }),
        ('Time Metrics', {
            'fields': ('total_processing_time_hours', 'total_wait_time_hours', 'total_downtime_hours', 'efficiency_percentage')
        }),
        ('Quality', {
            'fields': ('quality_holds_count', 'ncr_count')
        }),
        ('Delays', {
            'fields': ('avg_delay_minutes', 'top_delay_reason')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


# ============================================================================
# MAINTENANCE & EQUIPMENT
# ============================================================================

@admin.register(models.Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_code', 'name', 'department', 'status', 'is_maintenance_due', 'last_maintenance_date', 'next_maintenance_date']
    list_filter = ['department', 'status', 'equipment_type']
    search_fields = ['equipment_code', 'name', 'serial_number']
    date_hierarchy = 'installation_date'

    fieldsets = (
        ('Equipment Information', {
            'fields': ('equipment_code', 'name', 'equipment_type', 'status')
        }),
        ('Location', {
            'fields': ('department', 'location')
        }),
        ('Specifications', {
            'fields': ('manufacturer', 'model_number', 'serial_number', 'installation_date')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance_date', 'next_maintenance_date', 'maintenance_interval_days')
        }),
        ('Usage', {
            'fields': ('total_operating_hours',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(models.MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'equipment', 'request_type', 'priority', 'status', 'reported_at', 'downtime_hours']
    list_filter = ['request_type', 'priority', 'status', 'reported_at']
    search_fields = ['request_number', 'equipment__equipment_code', 'problem_description']
    autocomplete_fields = ['equipment', 'reported_by', 'assigned_to', 'affected_job_cards']
    date_hierarchy = 'reported_at'

    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'equipment', 'request_type', 'priority', 'status')
        }),
        ('Reported By', {
            'fields': ('reported_by', 'reported_by_name', 'reported_at')
        }),
        ('Problem Details', {
            'fields': ('problem_description', 'impact_on_production')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'assigned_at')
        }),
        ('Work Performed', {
            'fields': ('work_started_at', 'work_completed_at', 'work_performed', 'parts_used')
        }),
        ('Costs', {
            'fields': ('labor_hours', 'parts_cost', 'total_cost')
        }),
        ('Downtime', {
            'fields': ('downtime_start', 'downtime_end', 'downtime_hours')
        }),
        ('Impact', {
            'fields': ('affected_job_cards',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(models.ProcessExecutionLog)
class ProcessExecutionLogAdmin(admin.ModelAdmin):
    """Admin for process execution logs (audit trail)"""
    list_display = [
        'log_number', 'job_card', 'process_code', 'operator_name',
        'scanned_at', 'was_valid_sequence', 'was_corrected'
    ]
    list_filter = [
        'was_valid_sequence', 'was_corrected', 'department',
        'scanned_at'
    ]
    search_fields = [
        'log_number', 'job_card__jobcard_code', 'process_code',
        'operator_name'
    ]
    readonly_fields = [
        'log_number', 'scanned_at', 'created_at', 'was_valid_sequence',
        'validation_message'
    ]
    autocomplete_fields = ['job_card', 'job_route_step', 'operator']
    date_hierarchy = 'scanned_at'

    fieldsets = (
        ('Log Information', {
            'fields': ('log_number', 'scanned_at', 'created_at')
        }),
        ('Process Details', {
            'fields': (
                'job_card', 'job_route_step', 'process_code',
                'department', 'workstation'
            )
        }),
        ('Operator', {
            'fields': ('operator', 'operator_name')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at')
        }),
        ('Validation', {
            'fields': (
                'was_valid_sequence', 'expected_process_code',
                'validation_message'
            )
        }),
        ('Correction Status', {
            'fields': ('was_corrected', 'correction_request')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def has_add_permission(self, request):
        # Execution logs should only be created automatically
        return False

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of audit trail
        return request.user.is_superuser


@admin.register(models.ProcessCorrectionRequest)
class ProcessCorrectionRequestAdmin(admin.ModelAdmin):
    """Admin for process correction requests"""
    list_display = [
        'request_number', 'job_card', 'correction_type', 'status',
        'requested_by_name', 'requested_at', 'priority',
        'supervisor_reviewed_by'
    ]
    list_filter = [
        'status', 'correction_type', 'priority', 'requested_at',
        'supervisor_reviewed_at'
    ]
    search_fields = [
        'request_number', 'job_card__jobcard_code',
        'requested_by_name', 'reason'
    ]
    readonly_fields = [
        'request_number', 'requested_at', 'created_at', 'updated_at',
        'original_step_status', 'original_operator_name'
    ]
    autocomplete_fields = [
        'job_card', 'job_route_step', 'requested_by',
        'supervisor_reviewed_by', 'corrected_by', 'execution_log'
    ]
    date_hierarchy = 'requested_at'

    fieldsets = (
        ('Request Information', {
            'fields': (
                'request_number', 'status', 'priority',
                'requested_at', 'created_at', 'updated_at'
            )
        }),
        ('What Needs Correction', {
            'fields': (
                'job_card', 'job_route_step', 'execution_log',
                'correction_type'
            )
        }),
        ('Requested By', {
            'fields': ('requested_by', 'requested_by_name')
        }),
        ('Request Details', {
            'fields': ('reason', 'impact_description')
        }),
        ('Supervisor Review', {
            'fields': (
                'supervisor_reviewed_by', 'supervisor_reviewed_at',
                'supervisor_decision_notes'
            )
        }),
        ('Correction Execution', {
            'fields': (
                'corrected_at', 'corrected_by', 'correction_notes'
            )
        }),
        ('Original State (Audit)', {
            'fields': ('original_step_status', 'original_operator_name'),
            'classes': ('collapse',)
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of correction requests (audit trail)
        return request.user.is_superuser


# ============================================================================
# BOM & REPAIR HISTORY
# ============================================================================

class BOMItemInline(admin.TabularInline):
    """Inline BOM items for design revisions"""
    model = models.BOMItem
    extra = 1
    fields = ['item_type', 'part_number', 'description', 'quantity', 'unit', 'is_critical']


@admin.register(models.BOMItem)
class BOMItemAdmin(admin.ModelAdmin):
    """Admin for Bill of Materials items"""
    list_display = [
        'part_number', 'design_revision', 'item_type', 'quantity',
        'unit', 'manufacturer', 'is_critical'
    ]
    list_filter = ['item_type', 'is_critical', 'created_at']
    search_fields = [
        'part_number', 'description', 'manufacturer',
        'design_revision__mat_number'
    ]
    autocomplete_fields = ['design_revision']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('BOM Item', {
            'fields': (
                'design_revision', 'item_type', 'part_number', 'description'
            )
        }),
        ('Quantity', {
            'fields': ('quantity', 'unit')
        }),
        ('Supplier Information', {
            'fields': ('manufacturer', 'grade')
        }),
        ('Tracking', {
            'fields': ('is_critical',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(models.ActualBOM)
class ActualBOMAdmin(admin.ModelAdmin):
    """Admin for actual BOM usage tracking"""
    list_display = [
        'work_order', 'bom_item', 'planned_quantity',
        'actual_quantity', 'get_variance_display', 'lot_number'
    ]
    list_filter = ['recorded_at', 'bom_item__item_type']
    search_fields = [
        'work_order__wo_number', 'bom_item__part_number',
        'lot_number', 'serial_numbers'
    ]
    autocomplete_fields = ['work_order', 'bom_item', 'recorded_by']
    date_hierarchy = 'recorded_at'
    readonly_fields = ['recorded_at']

    def get_variance_display(self, obj):
        variance = obj.get_variance()
        if variance is not None:
            return f"{variance:+.2f}"
        return "—"
    get_variance_display.short_description = 'Variance'

    fieldsets = (
        ('Work Order', {
            'fields': ('work_order', 'bom_item')
        }),
        ('Quantities', {
            'fields': ('planned_quantity', 'actual_quantity')
        }),
        ('Traceability', {
            'fields': ('lot_number', 'serial_numbers')
        }),
        ('Variance', {
            'fields': ('variance_notes',)
        }),
        ('Recorded By', {
            'fields': ('recorded_by', 'recorded_at')
        }),
    )


@admin.register(models.RepairHistory)
class RepairHistoryAdmin(admin.ModelAdmin):
    """Admin for repair history tracking"""
    list_display = [
        'get_repair_display', 'bit_instance', 'work_order',
        'repair_index', 'cutters_replaced', 'nozzles_replaced',
        'repair_completed_date'
    ]
    list_filter = [
        'repair_index', 'hardfacing_applied', 'threads_repaired',
        'gauge_repaired', 'repair_completed_date'
    ]
    search_fields = [
        'bit_instance__serial_number', 'work_order__wo_number',
        'damage_description', 'repair_notes'
    ]
    autocomplete_fields = [
        'bit_instance', 'work_order', 'evaluation_summary',
        'route_template_used', 'previous_repair'
    ]
    date_hierarchy = 'repair_completed_date'
    readonly_fields = ['created_at', 'updated_at']

    def get_repair_display(self, obj):
        return f"{obj.bit_instance.serial_number}-R{obj.repair_index}"
    get_repair_display.short_description = 'Repair ID'

    fieldsets = (
        ('Repair Information', {
            'fields': (
                'bit_instance', 'work_order', 'repair_index',
                'evaluation_summary'
            )
        }),
        ('Usage Before Repair', {
            'fields': ('hours_on_bit', 'footage_drilled', 'damage_description')
        }),
        ('Work Performed', {
            'fields': (
                'cutters_replaced', 'nozzles_replaced', 'hardfacing_applied',
                'threads_repaired', 'gauge_repaired', 'balance_check'
            )
        }),
        ('Routing', {
            'fields': ('route_template_used',)
        }),
        ('Chain', {
            'fields': ('previous_repair',)
        }),
        ('Completion', {
            'fields': ('repair_completed_date', 'repair_notes')
        }),
    )


@admin.register(models.RepairDecision)
class RepairDecisionAdmin(admin.ModelAdmin):
    """Admin for repair routing decisions"""
    list_display = [
        'evaluation_summary', 'recommended_route',
        'needs_cutter_replacement', 'needs_hardfacing',
        'estimated_hours', 'estimated_cutter_count'
    ]
    list_filter = [
        'needs_cutter_replacement', 'needs_nozzle_replacement',
        'needs_hardfacing', 'needs_thread_repair',
        'needs_gauge_repair', 'needs_ndt', 'created_at'
    ]
    search_fields = [
        'evaluation_summary__job_card__jobcard_code',
        'decision_notes'
    ]
    autocomplete_fields = ['evaluation_summary', 'recommended_route', 'created_by']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Decision Based On', {
            'fields': ('evaluation_summary', 'recommended_route')
        }),
        ('Required Processes', {
            'fields': (
                'needs_cutter_replacement', 'needs_nozzle_replacement',
                'needs_hardfacing', 'needs_thread_repair',
                'needs_gauge_repair', 'needs_balance', 'needs_ndt'
            )
        }),
        ('Resource Estimates', {
            'fields': ('estimated_hours', 'estimated_cutter_count')
        }),
        ('Notes', {
            'fields': ('decision_notes',)
        }),
        ('Created By', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )


# Add BOM inline to BitDesignRevisionAdmin
BitDesignRevisionAdmin.inlines = [BOMItemInline]
