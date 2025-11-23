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
    list_display = ['design_code', 'bit_type', 'body_material', 'size_inch', 'blade_count', 'active', 'created_at']
    list_filter = ['bit_type', 'body_material', 'active', 'created_at']
    search_fields = ['design_code', 'description']
    date_hierarchy = 'created_at'
    list_per_page = 50
    fieldsets = (
        ('Basic Information', {
            'fields': ('design_code', 'bit_type', 'body_material', 'size_inch')
        }),
        ('Design Details', {
            'fields': ('blade_count', 'nozzle_count', 'description')
        }),
        ('Status', {
            'fields': ('active',)
        }),
    )


@admin.register(models.BitDesignRevision)
class BitDesignRevisionAdmin(admin.ModelAdmin):
    list_display = ['mat_number', 'design', 'level', 'effective_from', 'effective_to', 'active']
    list_filter = ['active', 'level', 'effective_from']
    search_fields = ['mat_number', 'design__design_code', 'remarks']
    date_hierarchy = 'effective_from'
    list_per_page = 50
    autocomplete_fields = ['design']
    fieldsets = (
        ('Revision Information', {
            'fields': ('design', 'mat_number', 'level')
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
