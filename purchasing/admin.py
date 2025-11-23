from django.contrib import admin
from .models import (
    PurchaseRequest, PurchaseRequestLine,
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine
)


class PurchaseRequestLineInline(admin.TabularInline):
    model = PurchaseRequestLine
    extra = 1
    raw_id_fields = ['item']
    fields = ['item', 'quantity', 'required_date', 'notes']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['pr_number', 'requested_by', 'request_date', 'status', 'created_at']
    list_filter = ['status', 'request_date']
    search_fields = ['pr_number', 'remarks']
    ordering = ['-request_date', '-pr_number']
    raw_id_fields = ['requested_by']
    date_hierarchy = 'request_date'
    inlines = [PurchaseRequestLineInline]
    fieldsets = (
        ('PR Information', {
            'fields': ('pr_number', 'requested_by', 'request_date', 'status')
        }),
        ('Remarks', {
            'fields': ('remarks',)
        }),
    )


@admin.register(PurchaseRequestLine)
class PurchaseRequestLineAdmin(admin.ModelAdmin):
    list_display = ['purchase_request', 'item', 'quantity', 'required_date']
    list_filter = ['required_date', 'purchase_request__status']
    search_fields = ['purchase_request__pr_number', 'item__item_code', 'item__name']
    raw_id_fields = ['purchase_request', 'item']
    ordering = ['-purchase_request__request_date']


class PurchaseOrderLineInline(admin.TabularInline):
    model = PurchaseOrderLine
    extra = 1
    raw_id_fields = ['item']
    fields = ['item', 'ordered_quantity', 'unit_price', 'expected_delivery_date', 'notes']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['po_number', 'supplier', 'order_date', 'status', 'currency', 'created_by', 'created_at']
    list_filter = ['status', 'order_date', 'currency', 'supplier']
    search_fields = ['po_number', 'supplier__name', 'notes', 'external_reference']
    ordering = ['-order_date', '-po_number']
    raw_id_fields = ['supplier', 'created_by']
    date_hierarchy = 'order_date'
    inlines = [PurchaseOrderLineInline]
    fieldsets = (
        ('PO Information', {
            'fields': ('po_number', 'supplier', 'order_date', 'status')
        }),
        ('Financial Details', {
            'fields': ('currency', 'payment_terms')
        }),
        ('Notes & References', {
            'fields': ('notes', 'external_reference', 'created_by')
        }),
    )


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = ['purchase_order', 'item', 'ordered_quantity', 'unit_price', 'line_total', 'expected_delivery_date']
    list_filter = ['expected_delivery_date', 'purchase_order__status']
    search_fields = ['purchase_order__po_number', 'item__item_code', 'item__name']
    raw_id_fields = ['purchase_order', 'item']
    ordering = ['-purchase_order__order_date']

    def line_total(self, obj):
        return f"{obj.line_total:.2f}"
    line_total.short_description = 'Line Total'


class GoodsReceiptLineInline(admin.TabularInline):
    model = GoodsReceiptLine
    extra = 1
    raw_id_fields = ['purchase_order_line', 'location', 'condition_type', 'ownership_type']
    fields = ['purchase_order_line', 'received_quantity', 'location', 'condition_type', 'ownership_type', 'notes']


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display = ['grn_number', 'purchase_order', 'receipt_date', 'received_by', 'created_at']
    list_filter = ['receipt_date']
    search_fields = ['grn_number', 'purchase_order__po_number', 'notes']
    ordering = ['-receipt_date', '-grn_number']
    raw_id_fields = ['purchase_order', 'received_by']
    date_hierarchy = 'receipt_date'
    inlines = [GoodsReceiptLineInline]
    fieldsets = (
        ('GRN Information', {
            'fields': ('grn_number', 'purchase_order', 'receipt_date', 'received_by')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(GoodsReceiptLine)
class GoodsReceiptLineAdmin(admin.ModelAdmin):
    list_display = ['goods_receipt', 'purchase_order_line', 'received_quantity', 'location', 'condition_type', 'ownership_type']
    list_filter = ['condition_type', 'ownership_type', 'location__warehouse']
    search_fields = ['goods_receipt__grn_number', 'purchase_order_line__item__item_code']
    raw_id_fields = ['goods_receipt', 'purchase_order_line', 'location', 'condition_type', 'ownership_type']
    ordering = ['-goods_receipt__receipt_date']
