from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, F
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
