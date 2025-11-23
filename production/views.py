"""
Production Department Views
Class-based views for CRUD operations and dashboards
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count, Prefetch
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
import qrcode
import io

from . import models


# ============================================================================
# DASHBOARD
# ============================================================================

class ProductionDashboardView(LoginRequiredMixin, TemplateView):
    """
    Main production dashboard with statistics and overview
    """
    template_name = 'production/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Work Orders statistics
        context['workorders_open'] = models.WorkOrder.objects.filter(
            status__in=['OPEN', 'IN_PROGRESS']
        ).count()
        context['workorders_urgent'] = models.WorkOrder.objects.filter(
            priority='URGENT',
            status__in=['OPEN', 'IN_PROGRESS']
        ).count()

        # Job Cards statistics
        context['jobcards_active'] = models.JobCard.objects.filter(
            status__in=['RELEASED', 'IN_PROGRESS']
        ).count()
        context['jobcards_qc_hold'] = models.JobCard.objects.filter(
            status='QC_HOLD'
        ).count()

        # Infiltration batches
        context['infiltration_in_progress'] = models.InfiltrationBatch.objects.filter(
            status__in=['LOADING', 'IN_FURNACE', 'COOLING']
        ).count()

        # Recent work orders
        context['recent_workorders'] = models.WorkOrder.objects.select_related(
            'design_revision__design'
        ).order_by('-created_at')[:10]

        # Active job cards by department
        context['jobcards_by_department'] = models.JobCard.objects.filter(
            status__in=['RELEASED', 'IN_PROGRESS']
        ).values('department').annotate(count=Count('id'))

        return context


# ============================================================================
# BIT DESIGN & INSTANCES
# ============================================================================

class BitDesignListView(LoginRequiredMixin, ListView):
    model = models.BitDesign
    template_name = 'production/bitdesign_list.html'
    context_object_name = 'designs'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()

        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(design_code__icontains=search) |
                Q(description__icontains=search)
            )

        # Filter by bit type
        bit_type = self.request.GET.get('bit_type')
        if bit_type:
            queryset = queryset.filter(bit_type=bit_type)

        # Filter by active status
        active = self.request.GET.get('active')
        if active == 'true':
            queryset = queryset.filter(active=True)

        return queryset.order_by('design_code')


class BitDesignDetailView(LoginRequiredMixin, DetailView):
    model = models.BitDesign
    template_name = 'production/bitdesign_detail.html'
    context_object_name = 'design'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['revisions'] = self.object.revisions.all()
        return context


class BitDesignCreateView(LoginRequiredMixin, CreateView):
    model = models.BitDesign
    template_name = 'production/bitdesign_form.html'
    fields = ['design_code', 'bit_type', 'body_material', 'size_inch',
              'blade_count', 'nozzle_count', 'description', 'active']
    success_url = reverse_lazy('production:bitdesign-list')

    def form_valid(self, form):
        messages.success(self.request, f'Bit Design {form.instance.design_code} created successfully.')
        return super().form_valid(form)


class BitDesignUpdateView(LoginRequiredMixin, UpdateView):
    model = models.BitDesign
    template_name = 'production/bitdesign_form.html'
    fields = ['design_code', 'bit_type', 'body_material', 'size_inch',
              'blade_count', 'nozzle_count', 'description', 'active']
    success_url = reverse_lazy('production:bitdesign-list')

    def form_valid(self, form):
        messages.success(self.request, f'Bit Design {form.instance.design_code} updated successfully.')
        return super().form_valid(form)


class BitInstanceListView(LoginRequiredMixin, ListView):
    model = models.BitInstance
    template_name = 'production/bitinstance_list.html'
    context_object_name = 'instances'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'design_revision__design'
        )

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(serial_number__icontains=search) |
                Q(design_revision__mat_number__icontains=search)
            )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')


class BitInstanceDetailView(LoginRequiredMixin, DetailView):
    model = models.BitInstance
    template_name = 'production/bitinstance_detail.html'
    context_object_name = 'instance'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['work_orders'] = self.object.work_orders.all().order_by('-created_at')
        return context


# ============================================================================
# WORK ORDERS
# ============================================================================

class WorkOrderListView(LoginRequiredMixin, ListView):
    model = models.WorkOrder
    template_name = 'production/workorder_list.html'
    context_object_name = 'workorders'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'design_revision__design', 'bit_instance'
        )

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(wo_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(rig__icontains=search)
            )

        # Filter by order type
        order_type = self.request.GET.get('order_type')
        if order_type:
            queryset = queryset.filter(order_type=order_type)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset.order_by('-created_at')


class WorkOrderDetailView(LoginRequiredMixin, DetailView):
    model = models.WorkOrder
    template_name = 'production/workorder_detail.html'
    context_object_name = 'workorder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['job_cards'] = self.object.job_cards.all().prefetch_related('route_steps')
        return context


class WorkOrderCreateView(LoginRequiredMixin, CreateView):
    model = models.WorkOrder
    template_name = 'production/workorder_form.html'
    fields = ['wo_number', 'order_type', 'bit_instance', 'design_revision',
              'customer_name', 'rig', 'well', 'field', 'rent_or_sale_type',
              'priority', 'status', 'received_date', 'due_date', 'remarks']

    def get_success_url(self):
        return reverse_lazy('production:workorder-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Work Order {form.instance.wo_number} created successfully.')
        return super().form_valid(form)


class WorkOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = models.WorkOrder
    template_name = 'production/workorder_form.html'
    fields = ['wo_number', 'order_type', 'bit_instance', 'design_revision',
              'customer_name', 'rig', 'well', 'field', 'rent_or_sale_type',
              'priority', 'status', 'received_date', 'due_date', 'remarks']

    def get_success_url(self):
        return reverse_lazy('production:workorder-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Work Order {form.instance.wo_number} updated successfully.')
        return super().form_valid(form)


# ============================================================================
# JOB CARDS
# ============================================================================

class JobCardListView(LoginRequiredMixin, ListView):
    model = models.JobCard
    template_name = 'production/jobcard_list.html'
    context_object_name = 'jobcards'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('work_order')

        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(jobcard_code__icontains=search) |
                Q(work_order__wo_number__icontains=search)
            )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department=department)

        return queryset.order_by('-created_at')


class JobCardDetailView(LoginRequiredMixin, DetailView):
    model = models.JobCard
    template_name = 'production/jobcard_detail.html'
    context_object_name = 'jobcard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['route_steps'] = self.object.route_steps.all().order_by('sequence')
        context['pauses'] = self.object.pauses.all()
        context['evaluations'] = self.object.evaluations.all()
        context['ndt_results'] = self.object.ndt_results.all()
        context['thread_inspections'] = self.object.thread_inspections.all()
        context['qr_codes'] = self.object.qr_codes.all()
        return context


class JobCardCreateView(LoginRequiredMixin, CreateView):
    model = models.JobCard
    template_name = 'production/jobcard_form.html'
    fields = ['jobcard_code', 'work_order', 'job_type', 'is_repair',
              'department', 'status', 'planned_start', 'planned_end',
              'current_workstation', 'notes']

    def get_success_url(self):
        return reverse_lazy('production:jobcard-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Job Card {form.instance.jobcard_code} created successfully.')
        return super().form_valid(form)


class JobCardUpdateView(LoginRequiredMixin, UpdateView):
    model = models.JobCard
    template_name = 'production/jobcard_form.html'
    fields = ['jobcard_code', 'work_order', 'job_type', 'is_repair',
              'department', 'status', 'planned_start', 'planned_end',
              'actual_start', 'actual_end', 'current_workstation', 'notes']

    def get_success_url(self):
        return reverse_lazy('production:jobcard-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Job Card {form.instance.jobcard_code} updated successfully.')
        return super().form_valid(form)


# ============================================================================
# ROUTE TEMPLATES
# ============================================================================

class RouteTemplateListView(LoginRequiredMixin, ListView):
    model = models.RouteTemplate
    template_name = 'production/routetemplate_list.html'
    context_object_name = 'routes'
    paginate_by = 50


class RouteTemplateDetailView(LoginRequiredMixin, DetailView):
    model = models.RouteTemplate
    template_name = 'production/routetemplate_detail.html'
    context_object_name = 'route'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.steps.all().order_by('sequence')
        return context


# ============================================================================
# INFILTRATION BATCHES
# ============================================================================

class InfiltrationBatchListView(LoginRequiredMixin, ListView):
    model = models.InfiltrationBatch
    template_name = 'production/infiltrationbatch_list.html'
    context_object_name = 'batches'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('-created_at')


class InfiltrationBatchDetailView(LoginRequiredMixin, DetailView):
    model = models.InfiltrationBatch
    template_name = 'production/infiltrationbatch_detail.html'
    context_object_name = 'batch'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.all().select_related('job_card')
        return context


class InfiltrationBatchCreateView(LoginRequiredMixin, CreateView):
    model = models.InfiltrationBatch
    template_name = 'production/infiltrationbatch_form.html'
    fields = ['batch_code', 'furnace_id', 'planned_start', 'planned_end',
              'temperature_profile', 'operator', 'operator_name', 'status', 'notes']

    def get_success_url(self):
        return reverse_lazy('production:infiltrationbatch-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, f'Infiltration Batch {form.instance.batch_code} created successfully.')
        return super().form_valid(form)


# ============================================================================
# QR CODE FUNCTIONALITY
# ============================================================================

def generate_qr_code_view(request, pk):
    """
    Generate QR code for a job card
    """
    jobcard = get_object_or_404(models.JobCard, pk=pk)

    # Create or get QR code
    qr_code, created = models.QRCode.objects.get_or_create(
        job_card=jobcard,
        defaults={'notes': f'Auto-generated for {jobcard.jobcard_code}'}
    )

    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Create the QR code URL
    qr_url = request.build_absolute_uri(
        f'/production/qr/{qr_code.code}/'
    )

    qr.add_data(qr_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Return image
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response


def qr_scan_view(request, code):
    """
    Handle QR code scanning - redirect to appropriate page
    """
    try:
        qr_code = get_object_or_404(models.QRCode, code=code)

        # Check expiration
        if qr_code.expires_at and qr_code.expires_at < timezone.now():
            messages.warning(request, 'This QR code has expired.')
            return redirect('production:dashboard')

        # Redirect to target
        if qr_code.job_card:
            return redirect('production:jobcard-detail', pk=qr_code.job_card.pk)
        elif qr_code.route_step:
            return redirect('production:jobcard-detail', pk=qr_code.route_step.job_card.pk)
        else:
            messages.error(request, 'QR code has no valid target.')
            return redirect('production:dashboard')

    except models.QRCode.DoesNotExist:
        messages.error(request, f'QR code {code} not found.')
        return redirect('production:dashboard')


# ============================================================================
# EVALUATION & QUALITY CONTROL
# ============================================================================

class EvaluationSummaryCreateView(LoginRequiredMixin, CreateView):
    """
    Create evaluation summary for a job card
    Automatically adjusts route based on evaluation results
    """
    model = models.EvaluationSummary
    template_name = 'production/evaluation_form.html'
    fields = ['job_card', 'evaluation_date', 'evaluator_name',
              'overall_condition', 'recommended_action', 'remarks']

    def get_initial(self):
        initial = super().get_initial()
        # Pre-fill job_card if provided in URL
        job_card_id = self.request.GET.get('job_card')
        if job_card_id:
            initial['job_card'] = job_card_id
        return initial

    def get_success_url(self):
        return reverse_lazy('production:jobcard-detail',
                          kwargs={'pk': self.object.job_card.pk})

    def form_valid(self, form):
        messages.success(
            self.request,
            f'Evaluation created for {form.instance.job_card.jobcard_code}. '
            f'Condition: {form.instance.get_overall_condition_display()}. '
            f'Route has been automatically adjusted.'
        )
        return super().form_valid(form)


class EvaluationSummaryListView(LoginRequiredMixin, ListView):
    """
    List all evaluations
    """
    model = models.EvaluationSummary
    template_name = 'production/evaluation_list.html'
    context_object_name = 'evaluations'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('job_card')

        # Filter by condition
        condition = self.request.GET.get('condition')
        if condition:
            queryset = queryset.filter(overall_condition=condition)

        return queryset.order_by('-evaluation_date')


# ============================================================================
# ROUTE MANAGEMENT
# ============================================================================

def regenerate_route_steps_view(request, pk):
    """
    Regenerate route steps for a job card
    Useful when job card configuration changes or evaluation results arrive
    """
    from .routing_logic import regenerate_route_steps

    jobcard = get_object_or_404(models.JobCard, pk=pk)

    if request.method == 'POST':
        try:
            steps = regenerate_route_steps(jobcard)
            messages.success(
                request,
                f'Successfully regenerated {len(steps)} route steps '
                f'for job card {jobcard.jobcard_code}.'
            )
        except Exception as e:
            messages.error(
                request,
                f'Failed to regenerate route steps: {str(e)}'
            )
        return redirect('production:jobcard-detail', pk=jobcard.pk)

    # GET request - show confirmation page
    return render(request, 'production/confirm_regenerate_route.html', {
        'jobcard': jobcard,
        'existing_steps': jobcard.route_steps.all().order_by('sequence')
    })


def update_route_step_status_view(request, pk, new_status):
    """
    Quick update of route step status
    Used for AJAX calls from shop floor
    """
    step = get_object_or_404(models.JobRouteStep, pk=pk)

    if new_status not in dict(models.RouteStepStatus.choices):
        return JsonResponse({'error': 'Invalid status'}, status=400)

    old_status = step.status
    step.status = new_status

    # Update timestamps
    if new_status == models.RouteStepStatus.IN_PROGRESS and not step.actual_start:
        step.actual_start = timezone.now()
    elif new_status == models.RouteStepStatus.DONE and not step.actual_end:
        step.actual_end = timezone.now()

    step.save()

    return JsonResponse({
        'success': True,
        'step_id': step.pk,
        'old_status': old_status,
        'new_status': new_status,
        'step_description': step.description
    })


# ============================================================================
# NCR / QUALITY ISSUES
# ============================================================================

class NCRCreateView(LoginRequiredMixin, CreateView):
    """
    Create Non-Conformance Report
    """
    model = models.NonConformanceReport
    template_name = 'production/ncr_form.html'
    fields = ['ncr_number', 'job_card', 'work_order', 'bit_instance',
              'severity', 'detected_at_process', 'detected_by_name',
              'description', 'root_cause', 'disposition',
              'corrective_action', 'status']

    def get_initial(self):
        initial = super().get_initial()
        job_card_id = self.request.GET.get('job_card')
        if job_card_id:
            job_card = models.JobCard.objects.get(pk=job_card_id)
            initial['job_card'] = job_card_id
            initial['work_order'] = job_card.work_order.pk
            initial['bit_instance'] = job_card.work_order.bit_instance.pk if job_card.work_order.bit_instance else None
        return initial

    def get_success_url(self):
        return reverse_lazy('production:ncr-list')

    def form_valid(self, form):
        messages.success(
            self.request,
            f'NCR {form.instance.ncr_number} created successfully.'
        )
        return super().form_valid(form)


class NCRListView(LoginRequiredMixin, ListView):
    """
    List all NCRs with filtering
    """
    model = models.NonConformanceReport
    template_name = 'production/ncr_list.html'
    context_object_name = 'ncrs'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'job_card', 'work_order'
        )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by severity
        severity = self.request.GET.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)

        return queryset.order_by('-reported_at')


class NCRDetailView(LoginRequiredMixin, DetailView):
    """
    NCR details
    """
    model = models.NonConformanceReport
    template_name = 'production/ncr_detail.html'
    context_object_name = 'ncr'


# ============================================================================
# PRODUCTION HOLDS
# ============================================================================

class ProductionHoldCreateView(LoginRequiredMixin, CreateView):
    """
    Create production hold
    """
    model = models.ProductionHold
    template_name = 'production/hold_form.html'
    fields = ['hold_number', 'job_card', 'work_order', 'hold_reason',
              'description', 'requires_approval', 'hold_placed_by_name']

    def get_initial(self):
        initial = super().get_initial()
        job_card_id = self.request.GET.get('job_card')
        if job_card_id:
            job_card = models.JobCard.objects.get(pk=job_card_id)
            initial['job_card'] = job_card_id
            initial['work_order'] = job_card.work_order.pk
        return initial

    def form_valid(self, form):
        # Update job card status
        if form.instance.job_card:
            form.instance.job_card.status = models.JobCardStatus.QC_HOLD
            form.instance.job_card.save()

        messages.warning(
            self.request,
            f'Production hold {form.instance.hold_number} created. '
            f'Job card status updated to QC Hold.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('production:jobcard-detail',
                          kwargs={'pk': self.object.job_card.pk})


class ProductionHoldListView(LoginRequiredMixin, ListView):
    """
    List all production holds
    """
    model = models.ProductionHold
    template_name = 'production/hold_list.html'
    context_object_name = 'holds'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('job_card', 'work_order')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Show active holds by default
        if not status:
            queryset = queryset.filter(status='ACTIVE')

        return queryset.order_by('-hold_placed_at')
