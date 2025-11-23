from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, F
from decimal import Decimal
from .models import (
    Supplier, ItemCategory, UnitOfMeasure, Item,
    Warehouse, Location, ConditionType, OwnershipType,
    StockLevel, StockTransaction
)


class InventoryDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view for inventory module."""
    template_name = 'inventory/dashboard.html'
    model = Item
    context_object_name = 'items'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = Item.objects.filter(active=True).count()
        context['total_warehouses'] = Warehouse.objects.filter(active=True).count()
        context['total_suppliers'] = Supplier.objects.filter(active=True).count()
        context['low_stock_items'] = Item.objects.filter(
            active=True,
            stock_levels__quantity__lt=F('reorder_level')
        ).distinct()[:5]
        return context


# Supplier Views
class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'inventory/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search) |
                Q(country__icontains=search)
            )
        return queryset


class SupplierDetailView(LoginRequiredMixin, DetailView):
    model = Supplier
    template_name = 'inventory/supplier_detail.html'
    context_object_name = 'supplier'


class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    fields = ['code', 'name', 'address', 'country', 'contact_person', 'phone', 'email', 'payment_terms', 'active']
    success_url = reverse_lazy('inventory:supplier_list')


class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'inventory/supplier_form.html'
    fields = ['code', 'name', 'address', 'country', 'contact_person', 'phone', 'email', 'payment_terms', 'active']
    success_url = reverse_lazy('inventory:supplier_list')


# Item Category Views
class ItemCategoryListView(LoginRequiredMixin, ListView):
    model = ItemCategory
    template_name = 'inventory/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20


class ItemCategoryCreateView(LoginRequiredMixin, CreateView):
    model = ItemCategory
    template_name = 'inventory/category_form.html'
    fields = ['code', 'name', 'description', 'parent']
    success_url = reverse_lazy('inventory:category_list')


# Item Views
class ItemListView(LoginRequiredMixin, ListView):
    model = Item
    template_name = 'inventory/item_list.html'
    context_object_name = 'items'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        item_type = self.request.GET.get('item_type')
        category = self.request.GET.get('category')

        if search:
            queryset = queryset.filter(
                Q(item_code__icontains=search) |
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        if item_type:
            queryset = queryset.filter(item_type=item_type)
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_types'] = Item.ITEM_TYPE_CHOICES
        context['categories'] = ItemCategory.objects.all()
        return context


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Item
    template_name = 'inventory/item_detail.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stock_levels'] = self.object.stock_levels.select_related(
            'location__warehouse', 'condition_type', 'ownership_type'
        )
        context['recent_transactions'] = self.object.transactions.select_related(
            'from_location', 'to_location', 'performed_by'
        )[:10]
        return context


class ItemCreateView(LoginRequiredMixin, CreateView):
    model = Item
    template_name = 'inventory/item_form.html'
    fields = ['item_code', 'name', 'category', 'unit_of_measure', 'description', 'item_type', 'active', 'reorder_level', 'preferred_supplier']
    success_url = reverse_lazy('inventory:item_list')


class ItemUpdateView(LoginRequiredMixin, UpdateView):
    model = Item
    template_name = 'inventory/item_form.html'
    fields = ['item_code', 'name', 'category', 'unit_of_measure', 'description', 'item_type', 'active', 'reorder_level', 'preferred_supplier']
    success_url = reverse_lazy('inventory:item_list')


# Warehouse Views
class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'inventory/warehouse_list.html'
    context_object_name = 'warehouses'
    paginate_by = 20


class WarehouseDetailView(LoginRequiredMixin, DetailView):
    model = Warehouse
    template_name = 'inventory/warehouse_detail.html'
    context_object_name = 'warehouse'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = self.object.locations.all()
        return context


class WarehouseCreateView(LoginRequiredMixin, CreateView):
    model = Warehouse
    template_name = 'inventory/warehouse_form.html'
    fields = ['code', 'name', 'address', 'description', 'active']
    success_url = reverse_lazy('inventory:warehouse_list')


class WarehouseUpdateView(LoginRequiredMixin, UpdateView):
    model = Warehouse
    template_name = 'inventory/warehouse_form.html'
    fields = ['code', 'name', 'address', 'description', 'active']
    success_url = reverse_lazy('inventory:warehouse_list')


# Location Views
class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'inventory/location_list.html'
    context_object_name = 'locations'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse = self.request.GET.get('warehouse')
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.filter(active=True)
        return context


class LocationCreateView(LoginRequiredMixin, CreateView):
    model = Location
    template_name = 'inventory/location_form.html'
    fields = ['warehouse', 'code', 'name', 'description', 'is_virtual']
    success_url = reverse_lazy('inventory:location_list')


class LocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Location
    template_name = 'inventory/location_form.html'
    fields = ['warehouse', 'code', 'name', 'description', 'is_virtual']
    success_url = reverse_lazy('inventory:location_list')


# Stock Level Views
class StockLevelListView(LoginRequiredMixin, ListView):
    model = StockLevel
    template_name = 'inventory/stock_list.html'
    context_object_name = 'stock_levels'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'item', 'location__warehouse', 'condition_type', 'ownership_type'
        )

        item_search = self.request.GET.get('item')
        warehouse = self.request.GET.get('warehouse')
        condition = self.request.GET.get('condition')
        ownership = self.request.GET.get('ownership')

        if item_search:
            queryset = queryset.filter(
                Q(item__item_code__icontains=item_search) |
                Q(item__name__icontains=item_search)
            )
        if warehouse:
            queryset = queryset.filter(location__warehouse_id=warehouse)
        if condition:
            queryset = queryset.filter(condition_type_id=condition)
        if ownership:
            queryset = queryset.filter(ownership_type_id=ownership)

        return queryset.filter(quantity__gt=0)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.filter(active=True)
        context['conditions'] = ConditionType.objects.all()
        context['ownerships'] = OwnershipType.objects.all()
        return context


# Stock Transaction Views
class StockTransactionListView(LoginRequiredMixin, ListView):
    model = StockTransaction
    template_name = 'inventory/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'item', 'from_location', 'to_location', 'performed_by'
        )

        transaction_type = self.request.GET.get('transaction_type')
        item_search = self.request.GET.get('item')

        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        if item_search:
            queryset = queryset.filter(
                Q(item__item_code__icontains=item_search) |
                Q(item__name__icontains=item_search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['transaction_types'] = StockTransaction.TRANSACTION_TYPE_CHOICES
        return context


# Stock Adjustment View
class StockAdjustmentView(LoginRequiredMixin, CreateView):
    """Create stock adjustment transactions."""
    model = StockTransaction
    template_name = 'inventory/stock_adjustment.html'
    fields = ['item', 'to_location', 'condition_type', 'ownership_type', 'quantity', 'reference', 'notes']
    success_url = reverse_lazy('inventory:transaction_list')

    def form_valid(self, form):
        form.instance.transaction_type = 'ADJUSTMENT'
        form.instance.performed_by = self.request.user
        form.instance.from_location = None

        # Save transaction
        response = super().form_valid(form)

        # Update stock level
        stock_level, created = StockLevel.objects.get_or_create(
            item=form.instance.item,
            location=form.instance.to_location,
            condition_type=form.instance.condition_type,
            ownership_type=form.instance.ownership_type,
            defaults={'quantity': 0}
        )
        stock_level.quantity += form.instance.quantity
        stock_level.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Stock Adjustment'
        return context


# Stock Transfer View
class StockTransferView(LoginRequiredMixin, CreateView):
    """Transfer stock between locations."""
    model = StockTransaction
    template_name = 'inventory/stock_transfer.html'
    fields = ['item', 'from_location', 'to_location', 'condition_type', 'ownership_type', 'quantity', 'reference', 'notes']
    success_url = reverse_lazy('inventory:transaction_list')

    def form_valid(self, form):
        form.instance.transaction_type = 'TRANSFER'
        form.instance.performed_by = self.request.user

        # Check if sufficient stock exists at from_location
        try:
            stock_level = StockLevel.objects.get(
                item=form.instance.item,
                location=form.instance.from_location,
                condition_type=form.instance.condition_type,
                ownership_type=form.instance.ownership_type
            )

            if stock_level.quantity < form.instance.quantity:
                form.add_error('quantity', f'Insufficient stock. Available: {stock_level.quantity}')
                return self.form_invalid(form)
        except StockLevel.DoesNotExist:
            form.add_error('from_location', 'No stock available at this location')
            return self.form_invalid(form)

        # Save transaction
        response = super().form_valid(form)

        # Decrease stock at from_location
        stock_level.quantity -= form.instance.quantity
        stock_level.save()

        # Increase stock at to_location
        to_stock, created = StockLevel.objects.get_or_create(
            item=form.instance.item,
            location=form.instance.to_location,
            condition_type=form.instance.condition_type,
            ownership_type=form.instance.ownership_type,
            defaults={'quantity': 0}
        )
        to_stock.quantity += form.instance.quantity
        to_stock.save()

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Stock Transfer'
        return context


# Low Stock Items View
class LowStockItemsView(LoginRequiredMixin, ListView):
    """View items with stock below reorder level."""
    model = Item
    template_name = 'inventory/low_stock_items.html'
    context_object_name = 'low_stock_items'
    paginate_by = 50

    def get_queryset(self):
        from django.db.models import Sum, F

        # Get items where total stock is below reorder level
        queryset = Item.objects.filter(active=True).annotate(
            total_stock=Sum('stock_levels__quantity')
        ).filter(
            total_stock__lt=F('reorder_level')
        ).select_related('category', 'unit_of_measure', 'preferred_supplier')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calculate urgency for each item
        for item in context['low_stock_items']:
            if item.total_stock is None:
                item.total_stock = 0
            item.stock_percentage = (item.total_stock / item.reorder_level * 100) if item.reorder_level > 0 else 0
            item.urgency = 'critical' if item.stock_percentage < 25 else 'warning' if item.stock_percentage < 50 else 'low'
        return context


# QR Code Views
class ItemQRCodeView(LoginRequiredMixin, DetailView):
    """Display QR code for an item."""
    model = Item
    template_name = 'inventory/item_qrcode.html'
    context_object_name = 'item'

    def get_context_data(self, **kwargs):
        from .utils import generate_qr_code, generate_item_qr_data

        context = super().get_context_data(**kwargs)
        qr_data = generate_item_qr_data(self.object)
        context['qr_code'] = generate_qr_code(qr_data)
        context['qr_data'] = qr_data
        return context


class LocationQRCodeView(LoginRequiredMixin, DetailView):
    """Display QR code for a location."""
    model = Location
    template_name = 'inventory/location_qrcode.html'
    context_object_name = 'location'

    def get_context_data(self, **kwargs):
        from .utils import generate_qr_code, generate_location_qr_data

        context = super().get_context_data(**kwargs)
        qr_data = generate_location_qr_data(self.object)
        context['qr_code'] = generate_qr_code(qr_data)
        context['qr_data'] = qr_data
        return context


# Export Views
from django.views import View
from .export_utils import (
    export_to_csv, export_to_excel,
    get_stock_export_fields, get_transaction_export_fields,
    get_items_export_fields, get_low_stock_export_fields
)
from datetime import datetime


class ExportStockView(LoginRequiredMixin, View):
    """Export stock levels to CSV or Excel."""

    def get(self, request):
        format_type = request.GET.get('format', 'excel')

        queryset = StockLevel.objects.filter(quantity__gt=0).select_related(
            'item', 'location__warehouse', 'condition_type', 'ownership_type'
        )

        # Apply filters
        warehouse = request.GET.get('warehouse')
        if warehouse:
            queryset = queryset.filter(location__warehouse_id=warehouse)

        filename = f"stock_levels_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fields = get_stock_export_fields()

        if format_type == 'csv':
            return export_to_csv(queryset, f"{filename}.csv", fields)
        else:
            return export_to_excel(queryset, f"{filename}.xlsx", fields, 'Stock Levels')


class ExportTransactionsView(LoginRequiredMixin, View):
    """Export stock transactions to CSV or Excel."""

    def get(self, request):
        format_type = request.GET.get('format', 'excel')

        queryset = StockTransaction.objects.all().select_related(
            'item', 'from_location', 'to_location', 'performed_by'
        )

        # Apply filters
        transaction_type = request.GET.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fields = get_transaction_export_fields()

        if format_type == 'csv':
            return export_to_csv(queryset, f"{filename}.csv", fields)
        else:
            return export_to_excel(queryset, f"{filename}.xlsx", fields, 'Transactions')


class ExportItemsView(LoginRequiredMixin, View):
    """Export items to CSV or Excel."""

    def get(self, request):
        format_type = request.GET.get('format', 'excel')

        queryset = Item.objects.filter(active=True).select_related(
            'category', 'unit_of_measure', 'preferred_supplier'
        )

        filename = f"items_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fields = get_items_export_fields()

        if format_type == 'csv':
            return export_to_csv(queryset, f"{filename}.csv", fields)
        else:
            return export_to_excel(queryset, f"{filename}.xlsx", fields, 'Items')


class ExportLowStockView(LoginRequiredMixin, View):
    """Export low stock items to CSV or Excel."""

    def get(self, request):
        from django.db.models import Sum, F

        format_type = request.GET.get('format', 'excel')

        queryset = Item.objects.filter(active=True).annotate(
            total_stock=Sum('stock_levels__quantity')
        ).filter(
            total_stock__lt=F('reorder_level')
        ).select_related('category', 'unit_of_measure', 'preferred_supplier')

        filename = f"low_stock_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        fields = get_low_stock_export_fields()

        if format_type == 'csv':
            return export_to_csv(queryset, f"{filename}.csv", fields)
        else:
            return export_to_excel(queryset, f"{filename}.xlsx", fields, 'Low Stock Items')


# Enhanced Dashboard View
import json
from django.db.models import Sum, Count


class EnhancedDashboardView(LoginRequiredMixin, ListView):
    """Enhanced dashboard with charts and analytics."""
    template_name = 'inventory/dashboard_enhanced.html'
    model = Item
    context_object_name = 'items'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        from django.db.models import F, Sum, Count, Q

        context = super().get_context_data(**kwargs)

        # Basic stats
        context['total_items'] = Item.objects.filter(active=True).count()
        context['total_warehouses'] = Warehouse.objects.filter(active=True).count()
        context['total_suppliers'] = Supplier.objects.filter(active=True).count()

        # Low stock items
        low_stock_qs = Item.objects.filter(active=True).annotate(
            total_stock=Sum('stock_levels__quantity')
        ).filter(
            Q(total_stock__lt=F('reorder_level')) | Q(total_stock__isnull=True)
        )
        context['low_stock_count'] = low_stock_qs.count()
        context['low_stock_items'] = low_stock_qs[:5]

        # Recent transactions
        context['recent_transactions'] = StockTransaction.objects.select_related(
            'item', 'to_location', 'performed_by'
        )[:10]

        # Stock by Category (for chart)
        category_stats = ItemCategory.objects.annotate(
            item_count=Count('items', filter=Q(items__active=True))
        ).filter(item_count__gt=0).order_by('-item_count')[:10]

        context['category_labels'] = json.dumps([cat.name for cat in category_stats])
        context['category_data'] = json.dumps([cat.item_count for cat in category_stats])

        # Stock by Warehouse (for chart)
        warehouse_stats = Warehouse.objects.filter(active=True).annotate(
            stock_count=Count('locations__stock_levels')
        ).order_by('-stock_count')

        context['warehouse_labels'] = json.dumps([wh.code for wh in warehouse_stats])
        context['warehouse_data'] = json.dumps([wh.stock_count for wh in warehouse_stats])

        return context

# ==================== Bulk Operations Views ====================

from django.contrib import messages
from .bulk_operations import BulkItemImporter, BulkStockAdjustment, BatchItemUpdater
from django.views import View


class BulkItemImportView(LoginRequiredMixin, View):
    """
    View for bulk importing items from Excel or CSV files.
    """
    template_name = 'inventory/bulk_item_import.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        uploaded_file = request.FILES.get('import_file')
        file_format = request.POST.get('format', 'excel')

        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return render(request, self.template_name)

        importer = BulkItemImporter(request.user)

        # Process based on format
        if file_format == 'excel':
            success = importer.import_from_excel(uploaded_file)
        else:
            success = importer.import_from_csv(uploaded_file)

        # Get summary
        summary = importer.get_summary()

        if success:
            messages.success(
                request,
                f"Import completed! Created: {summary['success_count']}, "
                f"Updated: {summary['update_count']}"
            )
        else:
            messages.warning(
                request,
                f"Import completed with errors. Created: {summary['success_count']}, "
                f"Updated: {summary['update_count']}, Errors: {summary['error_count']}"
            )

        return render(request, self.template_name, {'summary': summary})


class BulkStockAdjustmentView(LoginRequiredMixin, View):
    """
    View for bulk stock adjustments from Excel or CSV files.
    """
    template_name = 'inventory/bulk_stock_adjustment.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        uploaded_file = request.FILES.get('adjustment_file')
        file_format = request.POST.get('format', 'excel')

        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return render(request, self.template_name)

        adjuster = BulkStockAdjustment(request.user)

        # Process based on format
        if file_format == 'excel':
            success = adjuster.process_from_excel(uploaded_file)
        else:
            success = adjuster.process_from_csv(uploaded_file)

        # Get summary
        summary = adjuster.get_summary()

        if success:
            messages.success(
                request,
                f"Bulk adjustment completed! {summary['success_count']} adjustments processed."
            )
        else:
            messages.warning(
                request,
                f"Adjustment completed with errors. Processed: {summary['success_count']}, "
                f"Errors: {summary['error_count']}"
            )

        return render(request, self.template_name, {'summary': summary})


class BatchItemUpdateView(LoginRequiredMixin, View):
    """
    View for batch updating multiple items at once.
    """
    template_name = 'inventory/batch_item_update.html'

    def get(self, request):
        categories = ItemCategory.objects.all()
        suppliers = Supplier.objects.filter(active=True)
        items = Item.objects.filter(active=True)
        return render(request, self.template_name, {
            'categories': categories,
            'suppliers': suppliers,
            'items': items
        })

    def post(self, request):
        action = request.POST.get('action')
        item_ids = request.POST.getlist('item_ids')

        if not item_ids:
            messages.error(request, 'Please select at least one item.')
            return redirect('inventory:batch_item_update')

        # Convert to integers
        item_ids = [int(id) for id in item_ids]

        # Perform action
        try:
            if action == 'update_category':
                category_id = request.POST.get('new_category')
                if category_id:
                    category = ItemCategory.objects.get(id=category_id)
                    count = BatchItemUpdater.update_category(item_ids, category)
                    messages.success(request, f"Updated category for {count} items.")
                else:
                    messages.error(request, 'Please select a category.')

            elif action == 'update_reorder_level':
                new_level = request.POST.get('new_reorder_level')
                if new_level:
                    count = BatchItemUpdater.update_reorder_level(item_ids, Decimal(new_level))
                    messages.success(request, f"Updated reorder level for {count} items.")
                else:
                    messages.error(request, 'Please enter a reorder level.')

            elif action == 'activate':
                count = BatchItemUpdater.activate_items(item_ids)
                messages.success(request, f"Activated {count} items.")

            elif action == 'deactivate':
                count = BatchItemUpdater.deactivate_items(item_ids)
                messages.success(request, f"Deactivated {count} items.")

            elif action == 'update_supplier':
                supplier_id = request.POST.get('new_supplier')
                if supplier_id:
                    supplier = Supplier.objects.get(id=supplier_id)
                    count = BatchItemUpdater.update_supplier(item_ids, supplier)
                    messages.success(request, f"Updated supplier for {count} items.")
                else:
                    messages.error(request, 'Please select a supplier.')

            else:
                messages.error(request, 'Invalid action.')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect('inventory:batch_item_update')


# ==================== User Preferences Views ====================

from .models import UserPreferences


class UserPreferencesView(LoginRequiredMixin, View):
    """
    View for managing user preferences and settings.
    """
    template_name = 'inventory/user_preferences.html'

    def get(self, request):
        # Get or create preferences for the current user
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)
        return render(request, self.template_name, {'preferences': preferences})

    def post(self, request):
        preferences, created = UserPreferences.objects.get_or_create(user=request.user)

        # Update preferences from form
        preferences.dashboard_view = request.POST.get('dashboard_view', 'enhanced')
        preferences.items_per_page = int(request.POST.get('items_per_page', 20))
        preferences.receive_low_stock_emails = request.POST.get('receive_low_stock_emails') == 'on'
        preferences.low_stock_threshold = int(request.POST.get('low_stock_threshold', 25))
        preferences.default_export_format = request.POST.get('default_export_format', 'excel')
        preferences.show_qr_codes = request.POST.get('show_qr_codes') == 'on'
        preferences.language = request.POST.get('language', 'en')
        preferences.date_format = request.POST.get('date_format', 'YYYY-MM-DD')

        preferences.save()

        messages.success(request, 'Your preferences have been updated successfully!')
        return redirect('inventory:user_preferences')
