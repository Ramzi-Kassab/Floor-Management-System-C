"""
Views for quality control, expiry management, and item lifecycle.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Sum, F, Count
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .quality_control import (
    QualityInspection, ItemBatch, DefectiveItemDisposition,
    UsedItemTracking, ExpiredItemAction
)
from .models import Item, StockLevel, Location, ConditionType
from purchasing.models import GoodsReceiptLine


# ==================== Quality Inspection Views ====================

class QualityInspectionDashboardView(LoginRequiredMixin, View):
    """Dashboard for quality control activities."""
    template_name = 'inventory/quality_dashboard.html'

    def get(self, request):
        # Pending inspections
        pending_grn_inspections = GoodsReceiptLine.objects.filter(
            quality_inspections__isnull=True
        ).count()

        # Recent inspections
        recent_inspections = QualityInspection.objects.select_related(
            'item', 'inspected_by'
        )[:10]

        # Inspection statistics
        last_30_days = date.today() - timedelta(days=30)
        inspection_stats = QualityInspection.objects.filter(
            inspection_date__gte=last_30_days
        ).aggregate(
            total=Count('id'),
            passed=Count('id', filter=Q(inspection_result='PASS')),
            rejected=Count('id', filter=Q(inspection_result='REJECT')),
            rework=Count('id', filter=Q(inspection_result='REWORK')),
        )

        # Calculate pass rate
        if inspection_stats['total'] > 0:
            pass_rate = (inspection_stats['passed'] / inspection_stats['total']) * 100
        else:
            pass_rate = 0

        # Items in quarantine
        quarantined_batches = ItemBatch.objects.filter(is_quarantined=True).count()

        # Pending dispositions
        pending_dispositions = DefectiveItemDisposition.objects.filter(
            status='PENDING'
        ).count()

        context = {
            'pending_grn_inspections': pending_grn_inspections,
            'recent_inspections': recent_inspections,
            'inspection_stats': inspection_stats,
            'pass_rate': pass_rate,
            'quarantined_batches': quarantined_batches,
            'pending_dispositions': pending_dispositions,
        }

        return render(request, self.template_name, context)


class QualityInspectionListView(LoginRequiredMixin, ListView):
    """List all quality inspections."""
    model = QualityInspection
    template_name = 'inventory/quality_inspection_list.html'
    context_object_name = 'inspections'
    paginate_by = 25

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'item', 'inspected_by'
        )

        # Filter by result
        result = self.request.GET.get('result')
        if result:
            queryset = queryset.filter(inspection_result=result)

        # Filter by type
        inspection_type = self.request.GET.get('type')
        if inspection_type:
            queryset = queryset.filter(inspection_type=inspection_type)

        return queryset


# ==================== Expiry Management Views ====================

class ExpiryManagementDashboardView(LoginRequiredMixin, View):
    """Dashboard for managing expiry dates and expired items."""
    template_name = 'inventory/expiry_dashboard.html'

    def get(self, request):
        today = date.today()

        # Already expired
        expired_batches = ItemBatch.objects.filter(
            expiry_date__lt=today,
            is_expired=False  # Not yet marked as expired
        ).select_related('item', 'supplier')

        # Expiring soon (next 30 days)
        expiring_soon = ItemBatch.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=30)
        ).select_related('item', 'supplier').order_by('expiry_date')

        # Expiring this week (next 7 days)
        expiring_this_week = ItemBatch.objects.filter(
            expiry_date__gte=today,
            expiry_date__lte=today + timedelta(days=7)
        ).select_related('item').order_by('expiry_date')

        # Items with no expiry date set (that should have one)
        # This would need business logic to determine which items require expiry tracking
        missing_expiry = ItemBatch.objects.filter(
            expiry_date__isnull=True,
            item__item_type__in=['MATRIX_POWDER', 'CONSUMABLE', 'HARDFACING']  # Items that typically expire
        ).count()

        # Pending expiry actions
        pending_actions = ExpiredItemAction.objects.filter(
            approved_by__isnull=True
        ).count()

        # FEFO recommendations (First Expired First Out)
        fefo_recommendations = self._get_fefo_recommendations()

        context = {
            'expired_batches': expired_batches,
            'expiring_soon': expiring_soon,
            'expiring_this_week': expiring_this_week,
            'missing_expiry': missing_expiry,
            'pending_actions': pending_actions,
            'fefo_recommendations': fefo_recommendations,
        }

        return render(request, self.template_name, context)

    def _get_fefo_recommendations(self):
        """Get recommendations for which batches to use first based on expiry."""
        today = date.today()

        # Get items with multiple batches
        items_with_batches = ItemBatch.objects.filter(
            expiry_date__gte=today
        ).values('item').annotate(
            batch_count=Count('id')
        ).filter(batch_count__gt=1)

        recommendations = []
        for item_data in items_with_batches[:10]:  # Limit to 10 items
            item = Item.objects.get(pk=item_data['item'])
            batches = ItemBatch.objects.filter(
                item=item,
                expiry_date__gte=today
            ).order_by('expiry_date')[:3]  # Show 3 oldest batches

            if batches:
                recommendations.append({
                    'item': item,
                    'batches': batches,
                    'oldest_expiry': batches[0].expiry_date
                })

        return recommendations


class ExpiredItemActionCreateView(LoginRequiredMixin, View):
    """Create action for expired items."""
    template_name = 'inventory/expired_item_action_create.html'

    def get(self, request, batch_pk):
        batch = get_object_or_404(ItemBatch, pk=batch_pk)

        # Get current stock for this batch
        current_stock = batch.get_stock_in_batch()

        return render(request, self.template_name, {
            'batch': batch,
            'current_stock': current_stock,
            'action_types': ExpiredItemAction.ACTION_TYPE_CHOICES,
        })

    def post(self, request, batch_pk):
        batch = get_object_or_404(ItemBatch, pk=batch_pk)

        # Generate action number
        today = date.today()
        count = ExpiredItemAction.objects.filter(
            action_number__startswith=f'EXP-{today:%Y%m%d}'
        ).count() + 1
        action_number = f'EXP-{today:%Y%m%d}-{count:04d}'

        # Create action
        action = ExpiredItemAction.objects.create(
            action_number=action_number,
            batch=batch,
            action_type=request.POST['action_type'],
            action_date=request.POST.get('action_date', today),
            quantity=Decimal(request.POST['quantity']),
            book_value=Decimal(request.POST.get('book_value', '0')),
            recovery_value=Decimal(request.POST.get('recovery_value', '0')),
            executed_by=request.user,
            reason=request.POST.get('reason', ''),
            notes=request.POST.get('notes', '')
        )

        # Calculate loss
        action.loss_amount = action.book_value - action.recovery_value
        action.save()

        messages.success(
            request,
            f'Expired item action {action_number} created. '
            f'Awaiting supervisor approval for write-off.'
        )

        return redirect('inventory:expiry_dashboard')


# ==================== Defective Item Views ====================

class DefectiveItemsListView(LoginRequiredMixin, ListView):
    """List all defective item dispositions."""
    model = DefectiveItemDisposition
    template_name = 'inventory/defective_items_list.html'
    context_object_name = 'dispositions'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'quality_inspection__item',
            'disposed_by'
        )

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        pending = DefectiveItemDisposition.objects.filter(status='PENDING').count()
        in_rework = DefectiveItemDisposition.objects.filter(
            disposition_type='REWORK',
            status='IN_PROGRESS'
        ).count()

        context['pending_count'] = pending
        context['in_rework_count'] = in_rework

        return context


class DefectReportView(LoginRequiredMixin, View):
    """Generate defect analysis report."""
    template_name = 'inventory/defect_report.html'

    def get(self, request):
        # Date range filter
        days = int(request.GET.get('days', 30))
        start_date = date.today() - timedelta(days=days)

        # Defect statistics
        defect_stats = QualityInspection.objects.filter(
            inspection_date__gte=start_date,
            inspection_result__in=['REWORK', 'REJECT', 'SCRAP']
        ).values(
            'defect_category'
        ).annotate(
            count=Count('id'),
            total_qty=Sum('quantity_rejected') + Sum('quantity_for_rework')
        ).order_by('-count')

        # Top defective items
        defective_items = QualityInspection.objects.filter(
            inspection_date__gte=start_date,
            inspection_result__in=['REWORK', 'REJECT']
        ).values(
            'item__item_code',
            'item__name'
        ).annotate(
            defect_count=Count('id'),
            total_rejected=Sum('quantity_rejected')
        ).order_by('-defect_count')[:10]

        # Supplier quality analysis
        supplier_quality = QualityInspection.objects.filter(
            inspection_date__gte=start_date,
            goods_receipt_line__isnull=False
        ).values(
            'goods_receipt_line__goods_receipt__purchase_order__supplier__name'
        ).annotate(
            total_inspections=Count('id'),
            passed=Count('id', filter=Q(inspection_result='PASS')),
            failed=Count('id', filter=Q(inspection_result__in=['REJECT', 'SCRAP']))
        )

        context = {
            'days': days,
            'defect_stats': defect_stats,
            'defective_items': defective_items,
            'supplier_quality': supplier_quality,
        }

        return render(request, self.template_name, context)


# ==================== Used Item Tracking Views ====================

class UsedItemsListView(LoginRequiredMixin, ListView):
    """List all used/second-hand items."""
    model = UsedItemTracking
    template_name = 'inventory/used_items_list.html'
    context_object_name = 'used_items'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('item')

        # Filter by condition grade
        grade = self.request.GET.get('grade')
        if grade:
            queryset = queryset.filter(condition_grade=grade)

        # Filter by serviceability
        serviceable = self.request.GET.get('serviceable')
        if serviceable == 'yes':
            queryset = queryset.filter(is_serviceable=True)
        elif serviceable == 'no':
            queryset = queryset.filter(is_serviceable=False)

        # Filter by maintenance due
        maintenance_due = self.request.GET.get('maintenance_due')
        if maintenance_due == 'yes':
            queryset = queryset.filter(
                next_maintenance_due__lte=date.today()
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        total_used = UsedItemTracking.objects.count()
        serviceable = UsedItemTracking.objects.filter(is_serviceable=True).count()
        maintenance_due = UsedItemTracking.objects.filter(
            next_maintenance_due__lte=date.today()
        ).count()
        under_warranty = UsedItemTracking.objects.filter(
            warranty_expiry__gte=date.today()
        ).count()

        context['total_used'] = total_used
        context['serviceable'] = serviceable
        context['maintenance_due'] = maintenance_due
        context['under_warranty'] = under_warranty

        return context


class MaintenanceScheduleView(LoginRequiredMixin, ListView):
    """Show maintenance schedule for used items."""
    model = UsedItemTracking
    template_name = 'inventory/maintenance_schedule.html'
    context_object_name = 'items'

    def get_queryset(self):
        # Items with maintenance due in next 30 days
        today = date.today()
        return UsedItemTracking.objects.filter(
            next_maintenance_due__lte=today + timedelta(days=30),
            is_serviceable=True
        ).select_related('item').order_by('next_maintenance_due')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Group by urgency
        today = date.today()
        overdue = self.get_queryset().filter(next_maintenance_due__lt=today)
        this_week = self.get_queryset().filter(
            next_maintenance_due__gte=today,
            next_maintenance_due__lte=today + timedelta(days=7)
        )
        this_month = self.get_queryset().filter(
            next_maintenance_due__gt=today + timedelta(days=7),
            next_maintenance_due__lte=today + timedelta(days=30)
        )

        context['overdue'] = overdue
        context['this_week'] = this_week
        context['this_month'] = this_month

        return context


# ==================== Quick Actions for Quality/Lifecycle ====================

class QualityQuickActionsView(LoginRequiredMixin, View):
    """Quick access menu for quality and lifecycle management."""
    template_name = 'inventory/quality_quick_actions.html'

    def get(self, request):
        # Counts for action cards
        pending_inspections = GoodsReceiptLine.objects.filter(
            quality_inspections__isnull=True
        ).count()

        expired_items = ItemBatch.objects.filter(
            expiry_date__lt=date.today()
        ).count()

        expiring_soon = ItemBatch.objects.filter(
            expiry_date__gte=date.today(),
            expiry_date__lte=date.today() + timedelta(days=7)
        ).count()

        defective_pending = DefectiveItemDisposition.objects.filter(
            status='PENDING'
        ).count()

        maintenance_overdue = UsedItemTracking.objects.filter(
            next_maintenance_due__lt=date.today()
        ).count()

        quarantined = ItemBatch.objects.filter(is_quarantined=True).count()

        context = {
            'pending_inspections': pending_inspections,
            'expired_items': expired_items,
            'expiring_soon': expiring_soon,
            'defective_pending': defective_pending,
            'maintenance_overdue': maintenance_overdue,
            'quarantined': quarantined,
        }

        return render(request, self.template_name, context)
