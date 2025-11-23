from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from .models import (
    PurchaseRequest, PurchaseRequestLine,
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine
)


class PurchasingDashboardView(LoginRequiredMixin, ListView):
    """Dashboard view for purchasing module."""
    template_name = 'purchasing/dashboard.html'
    model = PurchaseOrder
    context_object_name = 'recent_pos'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset()[:10]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_prs'] = PurchaseRequest.objects.count()
        context['total_pos'] = PurchaseOrder.objects.count()
        context['total_grns'] = GoodsReceipt.objects.count()
        context['pending_prs'] = PurchaseRequest.objects.filter(status__in=['DRAFT', 'SUBMITTED']).count()
        return context


# Purchase Request Views
class PurchaseRequestListView(LoginRequiredMixin, ListView):
    model = PurchaseRequest
    template_name = 'purchasing/pr_list.html'
    context_object_name = 'purchase_requests'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')

        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(pr_number__icontains=search) |
                Q(remarks__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PurchaseRequest.STATUS_CHOICES
        return context


class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseRequest
    template_name = 'purchasing/pr_detail.html'
    context_object_name = 'pr'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('item')
        return context


class PurchaseRequestCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseRequest
    template_name = 'purchasing/pr_form.html'
    fields = ['pr_number', 'requested_by', 'request_date', 'status', 'remarks']
    success_url = reverse_lazy('purchasing:pr_list')


class PurchaseRequestUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseRequest
    template_name = 'purchasing/pr_form.html'
    fields = ['pr_number', 'requested_by', 'request_date', 'status', 'remarks']
    success_url = reverse_lazy('purchasing:pr_list')


# Purchase Order Views
class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'purchasing/po_list.html'
    context_object_name = 'purchase_orders'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('supplier')
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        supplier = self.request.GET.get('supplier')

        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(po_number__icontains=search) |
                Q(notes__icontains=search)
            )
        if supplier:
            queryset = queryset.filter(supplier_id=supplier)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PurchaseOrder.STATUS_CHOICES
        from inventory.models import Supplier
        context['suppliers'] = Supplier.objects.filter(active=True)
        return context


class PurchaseOrderDetailView(LoginRequiredMixin, DetailView):
    model = PurchaseOrder
    template_name = 'purchasing/po_detail.html'
    context_object_name = 'po'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related('item')
        context['goods_receipts'] = self.object.goods_receipts.all()
        return context


class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    template_name = 'purchasing/po_form.html'
    fields = ['po_number', 'supplier', 'order_date', 'status', 'currency', 'payment_terms', 'notes', 'created_by']
    success_url = reverse_lazy('purchasing:po_list')


class PurchaseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    template_name = 'purchasing/po_form.html'
    fields = ['po_number', 'supplier', 'order_date', 'status', 'currency', 'payment_terms', 'notes', 'created_by']
    success_url = reverse_lazy('purchasing:po_list')


# Goods Receipt Views
class GoodsReceiptListView(LoginRequiredMixin, ListView):
    model = GoodsReceipt
    template_name = 'purchasing/grn_list.html'
    context_object_name = 'goods_receipts'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('purchase_order')
        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(
                Q(grn_number__icontains=search) |
                Q(purchase_order__po_number__icontains=search)
            )
        return queryset


class GoodsReceiptDetailView(LoginRequiredMixin, DetailView):
    model = GoodsReceipt
    template_name = 'purchasing/grn_detail.html'
    context_object_name = 'grn'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lines'] = self.object.lines.select_related(
            'purchase_order_line__item', 'location', 'condition_type', 'ownership_type'
        )
        return context


class GoodsReceiptCreateView(LoginRequiredMixin, CreateView):
    model = GoodsReceipt
    template_name = 'purchasing/grn_form.html'
    fields = ['grn_number', 'purchase_order', 'receipt_date', 'received_by', 'notes']
    success_url = reverse_lazy('purchasing:grn_list')


class GoodsReceiptUpdateView(LoginRequiredMixin, UpdateView):
    model = GoodsReceipt
    template_name = 'purchasing/grn_form.html'
    fields = ['grn_number', 'purchase_order', 'receipt_date', 'received_by', 'notes']
    success_url = reverse_lazy('purchasing:grn_list')
