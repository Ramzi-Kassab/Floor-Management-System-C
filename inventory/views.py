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
