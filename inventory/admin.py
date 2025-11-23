from django.contrib import admin
from .models import (
    Supplier, ItemCategory, UnitOfMeasure, Item,
    Warehouse, Location, ConditionType, OwnershipType,
    StockLevel, StockTransaction, UserPreferences,
    StockOperationApproval,
    QualityInspection, ItemBatch, DefectiveItemDisposition,
    UsedItemTracking, ExpiredItemAction,
    CompanyProfile, ItemCertificate, CustomsDeclaration,
    CustomsDeclarationLine, Shipment
)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'country', 'contact_person', 'email', 'active']
    list_filter = ['active', 'country']
    search_fields = ['code', 'name', 'contact_person', 'email']
    ordering = ['code']
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'active')
        }),
        ('Contact Details', {
            'fields': ('address', 'country', 'contact_person', 'phone', 'email')
        }),
        ('Payment Terms', {
            'fields': ('payment_terms',)
        }),
    )


@admin.register(ItemCategory)
class ItemCategoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'created_at']
    list_filter = ['parent']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']
    raw_id_fields = ['parent']


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_base_unit']
    list_filter = ['is_base_unit']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['item_code', 'name', 'category', 'item_type', 'unit_of_measure', 'active', 'reorder_level', 'vat_type', 'hs_code']
    list_filter = ['active', 'item_type', 'category', 'vat_type', 'country_of_origin', 'requires_saber_certificate']
    search_fields = ['item_code', 'name', 'description', 'external_reference', 'hs_code']
    ordering = ['item_code']
    raw_id_fields = ['preferred_supplier']
    fieldsets = (
        ('Basic Information', {
            'fields': ('item_code', 'name', 'category', 'item_type', 'active')
        }),
        ('Specifications', {
            'fields': ('description', 'unit_of_measure', 'reorder_level')
        }),
        ('Supplier', {
            'fields': ('preferred_supplier',)
        }),
        ('KSA Compliance', {
            'fields': ('hs_code', 'country_of_origin', 'vat_type', 'customs_duty_rate', 'requires_saber_certificate'),
            'description': 'Fields required for Saudi Arabia regulatory compliance'
        }),
        ('External Reference', {
            'fields': ('external_reference',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['code', 'name', 'address']
    ordering = ['code']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'warehouse', 'is_virtual', 'created_at']
    list_filter = ['warehouse', 'is_virtual']
    search_fields = ['code', 'name', 'description']
    ordering = ['warehouse__code', 'code']
    raw_id_fields = ['warehouse']


@admin.register(ConditionType)
class ConditionTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']


@admin.register(OwnershipType)
class OwnershipTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['code']


@admin.register(StockLevel)
class StockLevelAdmin(admin.ModelAdmin):
    list_display = ['item', 'location', 'condition_type', 'ownership_type', 'quantity', 'last_updated']
    list_filter = ['condition_type', 'ownership_type', 'location__warehouse']
    search_fields = ['item__item_code', 'item__name', 'location__code']
    ordering = ['item__item_code', 'location__code']
    raw_id_fields = ['item', 'location']
    readonly_fields = ['last_updated']


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ['performed_at', 'transaction_type', 'item', 'quantity', 'from_location', 'to_location', 'reference', 'performed_by']
    list_filter = ['transaction_type', 'condition_type', 'ownership_type', 'performed_at']
    search_fields = ['item__item_code', 'item__name', 'reference', 'notes']
    ordering = ['-performed_at']
    raw_id_fields = ['item', 'from_location', 'to_location', 'performed_by']
    readonly_fields = ['performed_at']
    date_hierarchy = 'performed_at'
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_type', 'item', 'quantity', 'reference')
        }),
        ('Locations', {
            'fields': ('from_location', 'to_location')
        }),
        ('Classification', {
            'fields': ('condition_type', 'ownership_type')
        }),
        ('Metadata', {
            'fields': ('performed_at', 'performed_by', 'notes', 'external_reference')
        }),
    )


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ['user', 'dashboard_view', 'items_per_page', 'receive_low_stock_emails', 'default_export_format']
    list_filter = ['dashboard_view', 'receive_low_stock_emails', 'default_export_format', 'language']
    search_fields = ['user__username', 'user__email']
    ordering = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Dashboard Preferences', {
            'fields': ('dashboard_view', 'items_per_page')
        }),
        ('Notification Preferences', {
            'fields': ('receive_low_stock_emails', 'low_stock_threshold')
        }),
        ('Export Preferences', {
            'fields': ('default_export_format',)
        }),
        ('Display Preferences', {
            'fields': ('show_qr_codes',)
        }),
        ('Localization', {
            'fields': ('language', 'date_format')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StockOperationApproval)
class StockOperationApprovalAdmin(admin.ModelAdmin):
    list_display = ['requested_by', 'operation_type', 'item', 'quantity', 'status', 'request_date', 'reviewed_by']
    list_filter = ['status', 'operation_type', 'request_date']
    search_fields = ['requested_by__username', 'item__item_code', 'item__name', 'reason_for_request']
    ordering = ['-request_date']
    raw_id_fields = ['transaction', 'requested_by', 'reviewed_by', 'item']
    readonly_fields = ['request_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('requested_by', 'request_date', 'operation_type')
        }),
        ('Operation Details', {
            'fields': ('item', 'quantity', 'transaction', 'reason_for_request')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'review_date', 'review_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_selected', 'reject_selected']
    
    def approve_selected(self, request, queryset):
        """Approve selected requests."""
        count = 0
        for approval in queryset.filter(status='PENDING'):
            approval.approve(request.user, 'Approved via admin action')
            count += 1
        self.message_user(request, f'{count} approval(s) approved.')
    approve_selected.short_description = 'Approve selected requests'
    
    def reject_selected(self, request, queryset):
        """Reject selected requests."""
        count = 0
        for approval in queryset.filter(status='PENDING'):
            approval.reject(request.user, 'Rejected via admin action')
            count += 1
        self.message_user(request, f'{count} approval(s) rejected.')
    reject_selected.short_description = 'Reject selected requests'


# ==================== Quality Control Admin ====================

@admin.register(QualityInspection)
class QualityInspectionAdmin(admin.ModelAdmin):
    list_display = ['inspection_number', 'inspection_date', 'item', 'inspection_type', 'inspection_result', 'inspected_by']
    list_filter = ['inspection_result', 'inspection_type', 'defect_severity', 'inspection_date']
    search_fields = ['inspection_number', 'item__item_code', 'item__name', 'defect_description']
    ordering = ['-inspection_date']
    raw_id_fields = ['item', 'inspected_by', 'goods_receipt_line']
    readonly_fields = ['inspection_date', 'created_at']
    date_hierarchy = 'inspection_date'

    fieldsets = (
        ('Inspection Information', {
            'fields': ('inspection_number', 'inspection_date', 'inspection_type', 'item')
        }),
        ('Results', {
            'fields': ('inspection_result', 'quantity_inspected', 'quantity_accepted', 'quantity_rejected', 'quantity_for_rework')
        }),
        ('Defect Details', {
            'fields': ('defect_category', 'defect_severity', 'defect_description')
        }),
        ('Reference', {
            'fields': ('goods_receipt_line', 'inspected_by', 'notes')
        }),
    )


@admin.register(ItemBatch)
class ItemBatchAdmin(admin.ModelAdmin):
    list_display = ['batch_number', 'item', 'manufacturing_date', 'expiry_date', 'is_expired', 'is_quarantined', 'supplier']
    list_filter = ['is_expired', 'is_quarantined', 'is_recalled', 'manufacturing_date', 'expiry_date']
    search_fields = ['batch_number', 'item__item_code', 'item__name', 'supplier_batch_number', 'certificate_number']
    ordering = ['-manufacturing_date']
    raw_id_fields = ['item', 'supplier']
    readonly_fields = ['created_at']
    date_hierarchy = 'expiry_date'

    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_number', 'item', 'supplier', 'supplier_batch_number')
        }),
        ('Dates', {
            'fields': ('manufacturing_date', 'expiry_date', 'shelf_life_days')
        }),
        ('Status', {
            'fields': ('is_quarantined', 'is_expired', 'is_recalled', 'quarantine_reason')
        }),
        ('Certificates', {
            'fields': ('certificate_number', 'certificate_url')
        }),
    )


@admin.register(DefectiveItemDisposition)
class DefectiveItemDispositionAdmin(admin.ModelAdmin):
    list_display = ['disposition_number', 'quality_inspection', 'disposition_type', 'quantity', 'status', 'disposition_date']
    list_filter = ['disposition_type', 'status', 'disposition_date']
    search_fields = ['disposition_number', 'quality_inspection__inspection_number', 'notes']
    ordering = ['-disposition_date']
    raw_id_fields = ['quality_inspection', 'disposed_by', 'rework_location']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'disposition_date'

    fieldsets = (
        ('Disposition Information', {
            'fields': ('disposition_number', 'quality_inspection', 'disposition_type', 'disposition_date', 'status')
        }),
        ('Quantities & Costs', {
            'fields': ('quantity', 'estimated_loss', 'recovery_value', 'rework_cost')
        }),
        ('Details', {
            'fields': ('disposed_by', 'completion_date', 'rework_location', 'return_authorization', 'notes')
        }),
    )


@admin.register(UsedItemTracking)
class UsedItemTrackingAdmin(admin.ModelAdmin):
    list_display = ['item', 'serial_number', 'condition_grade', 'hours_used', 'is_serviceable', 'next_maintenance_due', 'current_user']
    list_filter = ['condition_grade', 'is_serviceable', 'is_available', 'next_maintenance_due']
    search_fields = ['serial_number', 'item__item_code', 'item__name', 'current_user']
    ordering = ['item__item_code', 'serial_number']
    raw_id_fields = ['item']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Item Information', {
            'fields': ('item', 'serial_number', 'condition_grade')
        }),
        ('Purchase Information', {
            'fields': ('original_purchase_date', 'original_cost', 'current_book_value')
        }),
        ('Usage Tracking', {
            'fields': ('hours_used', 'cycles_used', 'is_serviceable', 'is_available', 'current_user')
        }),
        ('Inspections', {
            'fields': ('last_inspection_date', 'next_inspection_due')
        }),
        ('Maintenance', {
            'fields': ('last_maintenance_date', 'next_maintenance_due', 'maintenance_notes')
        }),
        ('Warranty', {
            'fields': ('warranty_expiry', 'warranty_terms')
        }),
        ('Documentation', {
            'fields': ('photo_url', 'documentation_url', 'notes')
        }),
    )


@admin.register(ExpiredItemAction)
class ExpiredItemActionAdmin(admin.ModelAdmin):
    list_display = ['action_number', 'batch', 'action_type', 'action_date', 'quantity', 'loss_amount', 'executed_by', 'approved_by']
    list_filter = ['action_type', 'action_date']
    search_fields = ['action_number', 'batch__batch_number', 'batch__item__item_code', 'reason']
    ordering = ['-action_date']
    raw_id_fields = ['batch', 'executed_by', 'approved_by']
    readonly_fields = ['action_date', 'created_at']
    date_hierarchy = 'action_date'

    fieldsets = (
        ('Action Information', {
            'fields': ('action_number', 'batch', 'action_type', 'action_date')
        }),
        ('Quantities & Values', {
            'fields': ('quantity', 'book_value', 'recovery_value', 'loss_amount')
        }),
        ('Details', {
            'fields': ('reason', 'notes', 'disposal_certificate', 'executed_by', 'approved_by')
        }),
    )


# ==================== KSA Compliance Admin ====================

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ['company_name_english', 'commercial_registration', 'vat_registration_number', 'is_cr_valid']
    search_fields = ['company_name_english', 'company_name_arabic', 'commercial_registration', 'vat_registration_number']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Company Names', {
            'fields': ('company_name_arabic', 'company_name_english')
        }),
        ('Legal Registration', {
            'fields': ('commercial_registration', 'cr_issue_date', 'cr_expiry_date')
        }),
        ('Tax Information', {
            'fields': ('vat_registration_number', 'vat_registration_date')
        }),
        ('Industrial License', {
            'fields': ('industrial_license_number', 'industrial_license_issue_date', 'industrial_license_expiry')
        }),
        ('Zakat', {
            'fields': ('zakat_certificate_number', 'zakat_certificate_expiry')
        }),
        ('Address', {
            'fields': ('address_arabic', 'address_english', 'city', 'postal_code', 'building_number', 'additional_number')
        }),
        ('Contact Information', {
            'fields': ('phone', 'mobile', 'email', 'website')
        }),
        ('E-Invoicing Settings', {
            'fields': ('einvoice_enabled', 'einvoice_environment', 'logo_url')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemCertificate)
class ItemCertificateAdmin(admin.ModelAdmin):
    list_display = ['item', 'certificate_type', 'certificate_number', 'issue_date', 'expiry_date', 'is_valid', 'is_expiring_soon']
    list_filter = ['certificate_type', 'is_valid', 'issuing_country', 'issue_date', 'expiry_date']
    search_fields = ['item__item_code', 'item__name', 'certificate_number', 'certificate_name', 'issuing_authority']
    ordering = ['-issue_date']
    raw_id_fields = ['item']
    readonly_fields = ['created_at', 'updated_at', 'days_until_expiry']
    date_hierarchy = 'expiry_date'

    fieldsets = (
        ('Certificate Information', {
            'fields': ('item', 'certificate_type', 'certificate_number', 'certificate_name')
        }),
        ('Dates', {
            'fields': ('issue_date', 'expiry_date', 'days_until_expiry')
        }),
        ('Issuing Authority', {
            'fields': ('issuing_authority', 'issuing_country')
        }),
        ('Status', {
            'fields': ('is_valid', 'certificate_url', 'notes')
        }),
    )


class CustomsDeclarationLineInline(admin.TabularInline):
    model = CustomsDeclarationLine
    extra = 1
    raw_id_fields = ['item']
    fields = ['line_number', 'item', 'hs_code', 'quantity', 'unit_price', 'customs_duty_rate', 'vat_rate']


@admin.register(CustomsDeclaration)
class CustomsDeclarationAdmin(admin.ModelAdmin):
    list_display = ['declaration_number', 'declaration_type', 'declaration_date', 'clearance_status', 'total_customs_value', 'total_amount_payable']
    list_filter = ['declaration_type', 'clearance_status', 'declaration_date', 'port_of_entry']
    search_fields = ['declaration_number', 'bill_of_lading', 'airway_bill', 'importer_exporter', 'supplier_name']
    ordering = ['-declaration_date']
    raw_id_fields = ['purchase_order', 'goods_receipt']
    readonly_fields = ['created_at', 'updated_at', 'total_amount_payable']
    date_hierarchy = 'declaration_date'
    inlines = [CustomsDeclarationLineInline]

    fieldsets = (
        ('Declaration Information', {
            'fields': ('declaration_number', 'declaration_type', 'declaration_date', 'clearance_status')
        }),
        ('References', {
            'fields': ('purchase_order', 'goods_receipt')
        }),
        ('Shipping Details', {
            'fields': ('bill_of_lading', 'airway_bill', 'container_number', 'port_of_entry', 'port_of_exit')
        }),
        ('Parties', {
            'fields': ('importer_exporter', 'importer_exporter_cr', 'supplier_name', 'supplier_country')
        }),
        ('Customs Broker', {
            'fields': ('customs_broker_name', 'customs_broker_license')
        }),
        ('Financial', {
            'fields': ('total_customs_value', 'total_customs_duty', 'total_vat', 'other_fees', 'total_amount_payable')
        }),
        ('Clearance', {
            'fields': ('submission_date', 'clearance_date')
        }),
        ('Documents', {
            'fields': ('commercial_invoice_url', 'packing_list_url', 'certificate_of_origin_url')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(CustomsDeclarationLine)
class CustomsDeclarationLineAdmin(admin.ModelAdmin):
    list_display = ['customs_declaration', 'line_number', 'item', 'hs_code', 'quantity', 'total_value', 'customs_duty_amount', 'vat_amount']
    list_filter = ['country_of_origin', 'customs_declaration__declaration_type']
    search_fields = ['customs_declaration__declaration_number', 'item__item_code', 'hs_code', 'description']
    ordering = ['customs_declaration', 'line_number']
    raw_id_fields = ['customs_declaration', 'item']

    fieldsets = (
        ('Line Information', {
            'fields': ('customs_declaration', 'line_number', 'item')
        }),
        ('Classification', {
            'fields': ('hs_code', 'description', 'country_of_origin')
        }),
        ('Quantities & Values', {
            'fields': ('quantity', 'unit_of_measure', 'unit_price', 'total_value')
        }),
        ('Duties & Taxes', {
            'fields': ('customs_duty_rate', 'customs_duty_amount', 'vat_rate', 'vat_amount')
        }),
        ('Certificates', {
            'fields': ('saber_certificate_number', 'saso_certificate_number')
        }),
    )


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ['shipment_number', 'carrier', 'waybill_number', 'status', 'destination_city', 'expected_delivery_date', 'is_delivered']
    list_filter = ['carrier', 'status', 'origin_city', 'destination_city', 'expected_delivery_date']
    search_fields = ['shipment_number', 'waybill_number', 'recipient_name', 'recipient_phone']
    ordering = ['-created_at']
    raw_id_fields = ['goods_receipt']
    readonly_fields = ['created_at', 'updated_at', 'total_charges']
    date_hierarchy = 'expected_delivery_date'

    fieldsets = (
        ('Shipment Information', {
            'fields': ('shipment_number', 'carrier', 'waybill_number', 'tracking_url')
        }),
        ('Reference', {
            'fields': ('goods_receipt',)
        }),
        ('Origin', {
            'fields': ('origin_address', 'origin_city')
        }),
        ('Destination', {
            'fields': ('destination_address', 'destination_city', 'recipient_name', 'recipient_phone')
        }),
        ('Package Details', {
            'fields': ('number_of_packages', 'total_weight_kg')
        }),
        ('Dates', {
            'fields': ('pickup_date', 'expected_delivery_date', 'actual_delivery_date')
        }),
        ('Status', {
            'fields': ('status', 'delivered_to')
        }),
        ('Costs', {
            'fields': ('freight_charges', 'insurance_charges', 'cod_amount', 'total_charges')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
