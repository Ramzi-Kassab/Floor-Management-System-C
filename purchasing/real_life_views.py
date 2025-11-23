"""
Views for handling goods returns, corrections, and stock reconciliation.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import date

from .models import (
    GoodsReturn, GoodsReturnLine, GRNCorrection,
    GoodsReceipt, GoodsReceiptLine, PurchaseOrder
)
from inventory.models import StockLevel, StockTransaction, Location, ConditionType


# ==================== Goods Return Views ====================

class GoodsReturnListView(LoginRequiredMixin, ListView):
    """List all goods returns."""
    model = GoodsReturn
    template_name = 'purchasing/goods_return_list.html'
    context_object_name = 'returns'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'goods_receipt', 'goods_receipt__purchase_order', 'returned_by'
        )

        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class GoodsReturnDetailView(LoginRequiredMixin, DetailView):
    """View details of a specific goods return."""
    model = GoodsReturn
    template_name = 'purchasing/goods_return_detail.html'
    context_object_name = 'goods_return'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['return_lines'] = self.object.return_lines.select_related(
            'goods_receipt_line__purchase_order_line__item',
            'condition_at_return',
            'location'
        )
        return context


class GoodsReturnCreateView(LoginRequiredMixin, View):
    """Create a new goods return from a GRN."""
    template_name = 'purchasing/goods_return_create.html'

    def get(self, request, grn_pk):
        grn = get_object_or_404(GoodsReceipt, pk=grn_pk)
        grn_lines = grn.receipt_lines.select_related(
            'purchase_order_line__item',
            'location',
            'condition_type'
        )
        conditions = ConditionType.objects.all()
        locations = Location.objects.filter(active=True)

        return render(request, self.template_name, {
            'grn': grn,
            'grn_lines': grn_lines,
            'conditions': conditions,
            'locations': locations,
            'return_reasons': GoodsReturn.RETURN_REASON_CHOICES,
        })

    def post(self, request, grn_pk):
        grn = get_object_or_404(GoodsReceipt, pk=grn_pk)

        with transaction.atomic():
            # Generate RTN number
            today = date.today()
            count = GoodsReturn.objects.filter(rtn_number__startswith=f'RTN-{today:%Y%m%d}').count() + 1
            rtn_number = f'RTN-{today:%Y%m%d}-{count:04d}'

            # Create goods return
            goods_return = GoodsReturn.objects.create(
                rtn_number=rtn_number,
                goods_receipt=grn,
                return_date=request.POST.get('return_date', today),
                return_reason=request.POST.get('return_reason'),
                returned_by=request.user,
                supplier_contact=request.POST.get('supplier_contact', ''),
                remarks=request.POST.get('remarks', '')
            )

            # Create return lines
            line_count = 0
            for key in request.POST:
                if key.startswith('return_qty_'):
                    line_id = key.replace('return_qty_', '')
                    return_qty = Decimal(request.POST[key] or '0')

                    if return_qty > 0:
                        grn_line = get_object_or_404(GoodsReceiptLine, pk=line_id)

                        GoodsReturnLine.objects.create(
                            goods_return=goods_return,
                            goods_receipt_line=grn_line,
                            return_quantity=return_qty,
                            unit_price=Decimal(request.POST.get(f'unit_price_{line_id}', '0')),
                            condition_at_return_id=request.POST.get(f'condition_{line_id}'),
                            location_id=request.POST.get(f'location_{line_id}'),
                            notes=request.POST.get(f'notes_{line_id}', '')
                        )
                        line_count += 1

            if line_count == 0:
                messages.error(request, 'Please specify at least one item to return.')
                return redirect('purchasing:goods_return_create', grn_pk=grn_pk)

            messages.success(request, f'Goods Return {rtn_number} created successfully with {line_count} items.')
            return redirect('purchasing:goods_return_detail', pk=goods_return.pk)


class GoodsReturnSubmitView(LoginRequiredMixin, View):
    """Submit a goods return to supplier."""

    def post(self, request, pk):
        goods_return = get_object_or_404(GoodsReturn, pk=pk)

        if goods_return.status != 'DRAFT':
            messages.error(request, 'Only draft returns can be submitted.')
            return redirect('purchasing:goods_return_detail', pk=pk)

        # Update status and process stock transactions
        with transaction.atomic():
            goods_return.status = 'SUBMITTED'
            goods_return.save()

            # Stock transactions will be created automatically by GoodsReturnLine.save()
            # We need to trigger them now
            for line in goods_return.return_lines.all():
                line.save()  # This will create the stock transactions

        messages.success(request, f'Return {goods_return.rtn_number} submitted successfully. Stock has been adjusted.')
        return redirect('purchasing:goods_return_detail', pk=pk)


# ==================== GRN Correction Views ====================

class GRNCorrectionListView(LoginRequiredMixin, ListView):
    """List all GRN corrections."""
    model = GRNCorrection
    template_name = 'purchasing/grn_correction_list.html'
    context_object_name = 'corrections'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'goods_receipt_line__goods_receipt',
            'corrected_by'
        )

        # Filter by approval status
        approved = self.request.GET.get('approved')
        if approved == 'yes':
            queryset = queryset.filter(approved=True)
        elif approved == 'no':
            queryset = queryset.filter(approved=False)

        return queryset


class GRNCorrectionCreateView(LoginRequiredMixin, View):
    """Create a correction for a GRN line."""
    template_name = 'purchasing/grn_correction_create.html'

    def get(self, request, grn_line_pk):
        grn_line = get_object_or_404(GoodsReceiptLine, pk=grn_line_pk)
        locations = Location.objects.filter(active=True)
        conditions = ConditionType.objects.all()

        return render(request, self.template_name, {
            'grn_line': grn_line,
            'locations': locations,
            'conditions': conditions,
            'correction_types': GRNCorrection.CORRECTION_TYPE_CHOICES,
        })

    def post(self, request, grn_line_pk):
        grn_line = get_object_or_404(GoodsReceiptLine, pk=grn_line_pk)

        # Generate correction number
        today = date.today()
        count = GRNCorrection.objects.filter(correction_number__startswith=f'CORR-{today:%Y%m%d}').count() + 1
        correction_number = f'CORR-{today:%Y%m%d}-{count:04d}'

        correction = GRNCorrection.objects.create(
            correction_number=correction_number,
            goods_receipt_line=grn_line,
            correction_type=request.POST['correction_type'],
            correction_date=request.POST.get('correction_date', today),
            corrected_by=request.user,
            original_quantity=grn_line.received_quantity,
            original_location=grn_line.location,
            corrected_quantity=request.POST.get('corrected_quantity') or None,
            corrected_location_id=request.POST.get('corrected_location') or None,
            corrected_condition_id=request.POST.get('corrected_condition') or None,
            reason=request.POST['reason']
        )

        messages.success(request, f'Correction {correction_number} created. Awaiting approval.')
        return redirect('purchasing:grn_correction_detail', pk=correction.pk)


class GRNCorrectionDetailView(LoginRequiredMixin, DetailView):
    """View details of a GRN correction."""
    model = GRNCorrection
    template_name = 'purchasing/grn_correction_detail.html'
    context_object_name = 'correction'


class GRNCorrectionApproveView(LoginRequiredMixin, View):
    """Approve and apply a GRN correction."""

    def post(self, request, pk):
        correction = get_object_or_404(GRNCorrection, pk=pk)

        if correction.approved:
            messages.warning(request, 'This correction has already been approved.')
            return redirect('purchasing:grn_correction_detail', pk=pk)

        try:
            with transaction.atomic():
                correction.approved = True
                correction.approved_by = request.user
                correction.approved_at = timezone.now()
                correction.save()

                # Apply the correction (creates stock transactions)
                correction.apply_correction()

            messages.success(request, f'Correction {correction.correction_number} approved and applied successfully.')
        except Exception as e:
            messages.error(request, f'Error applying correction: {str(e)}')

        return redirect('purchasing:grn_correction_detail', pk=pk)


# ==================== Quick Actions for Real-Life Scenarios ====================

class WrongItemReceivedView(LoginRequiredMixin, View):
    """Handle scenario: Wrong item was received."""
    template_name = 'purchasing/wrong_item_received.html'

    def get(self, request, grn_line_pk):
        grn_line = get_object_or_404(GoodsReceiptLine, pk=grn_line_pk)
        return render(request, self.template_name, {'grn_line': grn_line})

    def post(self, request, grn_line_pk):
        grn_line = get_object_or_404(GoodsReceiptLine, pk=grn_line_pk)
        action = request.POST.get('action')

        if action == 'return':
            # Redirect to create return
            return redirect('purchasing:goods_return_create', grn_pk=grn_line.goods_receipt.pk)
        elif action == 'correction':
            # Create a correction record
            return redirect('purchasing:grn_correction_create', grn_line_pk=grn_line.pk)

        return redirect('purchasing:grn_detail', pk=grn_line.goods_receipt.pk)


class QuickActionsMenuView(LoginRequiredMixin, View):
    """Menu for common real-life scenarios."""
    template_name = 'purchasing/quick_actions_menu.html'

    def get(self, request):
        recent_grns = GoodsReceipt.objects.filter(
            status='RECEIVED'
        ).select_related('purchase_order').order_by('-receipt_date')[:10]

        pending_returns = GoodsReturn.objects.filter(
            status__in=['DRAFT', 'SUBMITTED']
        ).count()

        pending_corrections = GRNCorrection.objects.filter(
            approved=False
        ).count()

        return render(request, self.template_name, {
            'recent_grns': recent_grns,
            'pending_returns': pending_returns,
            'pending_corrections': pending_corrections,
        })
