from django.contrib import admin
from .models import (
    Supplier, ItemCategory, UnitOfMeasure, Item,
    Warehouse, Location, ConditionType, OwnershipType,
    StockLevel, StockTransaction, UserPreferences
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
    list_display = ['item_code', 'name', 'category', 'item_type', 'unit_of_measure', 'active', 'reorder_level']
    list_filter = ['active', 'item_type', 'category']
    search_fields = ['item_code', 'name', 'description', 'external_reference']
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
