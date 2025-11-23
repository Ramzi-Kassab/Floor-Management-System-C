from django.contrib import admin
from .models import (
    PurchaseRequest, PurchaseRequestLine,
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine,
    GoodsReturn, GoodsReturnLine,
    GRNCorrection
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


# ==================== Goods Return Admin ====================

class GoodsReturnLineInline(admin.TabularInline):
    model = GoodsReturnLine
    extra = 0
    raw_id_fields = ['goods_receipt_line', 'condition_at_return', 'location']
    fields = ['goods_receipt_line', 'return_quantity', 'unit_price', 'condition_at_return', 'location', 'notes']
    readonly_fields = ['goods_receipt_line']


@admin.register(GoodsReturn)
class GoodsReturnAdmin(admin.ModelAdmin):
    list_display = ['rtn_number', 'goods_receipt', 'return_date', 'return_reason', 'status', 'returned_by', 'total_return_value']
    list_filter = ['status', 'return_reason', 'return_date']
    search_fields = ['rtn_number', 'goods_receipt__grn_number', 'supplier_contact', 'remarks']
    ordering = ['-return_date', '-rtn_number']
    raw_id_fields = ['goods_receipt', 'returned_by']
    date_hierarchy = 'return_date'
    inlines = [GoodsReturnLineInline]
    readonly_fields = ['total_return_value']
    
    fieldsets = (
        ('Return Information', {
            'fields': ('rtn_number', 'goods_receipt', 'return_date', 'return_reason', 'status')
        }),
        ('Supplier Communication', {
            'fields': ('supplier_contact', 'supplier_approval_ref', 'credit_note_number', 'credit_note_amount')
        }),
        ('User & Notes', {
            'fields': ('returned_by', 'remarks')
        }),
        ('Summary', {
            'fields': ('total_return_value',),
            'classes': ('collapse',)
        }),
    )


@admin.register(GoodsReturnLine)
class GoodsReturnLineAdmin(admin.ModelAdmin):
    list_display = ['goods_return', 'item', 'return_quantity', 'unit_price', 'line_value', 'condition_at_return']
    list_filter = ['condition_at_return', 'goods_return__status']
    search_fields = ['goods_return__rtn_number', 'goods_receipt_line__purchase_order_line__item__item_code']
    raw_id_fields = ['goods_return', 'goods_receipt_line', 'condition_at_return', 'location']
    ordering = ['-goods_return__return_date']
    
    def line_value(self, obj):
        return f"{obj.line_value:.2f}"
    line_value.short_description = 'Line Value'


# ==================== GRN Correction Admin ====================

@admin.register(GRNCorrection)
class GRNCorrectionAdmin(admin.ModelAdmin):
    list_display = ['correction_number', 'goods_receipt_line', 'correction_type', 'correction_date', 'approved', 'corrected_by']
    list_filter = ['correction_type', 'approved', 'correction_date']
    search_fields = ['correction_number', 'goods_receipt_line__goods_receipt__grn_number', 'reason']
    ordering = ['-correction_date', '-correction_number']
    raw_id_fields = ['goods_receipt_line', 'corrected_by', 'approved_by', 'original_location', 'corrected_location', 'corrected_condition']
    date_hierarchy = 'correction_date'
    readonly_fields = ['adjustment_quantity', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Correction Information', {
            'fields': ('correction_number', 'goods_receipt_line', 'correction_type', 'correction_date', 'corrected_by')
        }),
        ('Original Values', {
            'fields': ('original_quantity', 'original_location')
        }),
        ('Corrected Values', {
            'fields': ('corrected_quantity', 'corrected_location', 'corrected_condition')
        }),
        ('Calculated', {
            'fields': ('adjustment_quantity',),
            'classes': ('collapse',)
        }),
        ('Reason & Approval', {
            'fields': ('reason', 'approved', 'approved_by', 'approved_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set approved_by when approval is changed."""
        if not change:
            obj.save()
        else:
            if obj.approved and not obj.approved_by:
                obj.approved_by = request.user
                from django.utils import timezone
                obj.approved_at = timezone.now()
            obj.save()
            
            # Apply correction if newly approved
            if obj.approved and 'approved' in form.changed_data:
                try:
                    obj.apply_correction()
                except Exception as e:
                    from django.contrib import messages
                    messages.error(request, f"Error applying correction: {str(e)}")
