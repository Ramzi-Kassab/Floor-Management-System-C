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


class JobCardPrintView(LoginRequiredMixin, DetailView):
    """
    Printable job card view with route sheet and QR codes for each process
    """
    model = models.JobCard
    template_name = 'production/jobcard_print.html'
    context_object_name = 'jobcard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        route_steps = self.object.route_steps.all().order_by('sequence')

        # Generate QR codes for each route step
        steps_with_qr = []
        for step in route_steps:
            # Get or create QR code for this route step
            qr_code, created = models.QRCode.objects.get_or_create(
                route_step=step,
                defaults={
                    'code': f'JC-{self.object.jobcard_code}-STEP-{step.sequence}',
                    'job_card': self.object,
                }
            )
            steps_with_qr.append({
                'step': step,
                'qr_code': qr_code,
            })

        context['steps_with_qr'] = steps_with_qr
        context['route_steps'] = route_steps
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
    Generate QR code for a job card or specific route step
    Query parameter: step=<route_step_id> for step-specific QR codes
    """
    jobcard = get_object_or_404(models.JobCard, pk=pk)

    # Check if this is for a specific route step
    step_id = request.GET.get('step')
    if step_id:
        # Generate QR code for specific route step
        route_step = get_object_or_404(models.JobRouteStep, pk=step_id, job_card=jobcard)
        qr_code, created = models.QRCode.objects.get_or_create(
            route_step=route_step,
            defaults={
                'code': f'JC-{jobcard.jobcard_code}-STEP-{route_step.sequence}',
                'job_card': jobcard,
                'notes': f'Auto-generated for {jobcard.jobcard_code} - {route_step.process_code}'
            }
        )
    else:
        # Generate QR code for entire job card
        qr_code, created = models.QRCode.objects.get_or_create(
            job_card=jobcard,
            route_step=None,
            defaults={
                'code': f'JC-{jobcard.jobcard_code}',
                'notes': f'Auto-generated for {jobcard.jobcard_code}'
            }
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
    Handle QR code scanning with process validation and dual-scan time tracking
    - Phone-based operator recognition (from query param, session, or header)
    - First scan: starts process timing (PENDING → IN_PROGRESS)
    - Second scan: ends process timing (IN_PROGRESS → DONE)
    """
    try:
        qr_code = get_object_or_404(models.QRCode, code=code)

        # Check expiration
        if qr_code.expires_at and qr_code.expires_at < timezone.now():
            messages.warning(request, 'This QR code has expired.')
            return redirect('production:dashboard')

        # Detect operator by phone number (query param > session > header)
        operator_phone = (
            request.GET.get('phone') or
            request.session.get('operator_phone') or
            request.META.get('HTTP_X_OPERATOR_PHONE')
        )

        operator = None
        if operator_phone:
            try:
                operator = models.Employee.objects.get(phone=operator_phone)
                # Store in session for future scans
                request.session['operator_phone'] = operator_phone
            except models.Employee.DoesNotExist:
                messages.warning(request, f'Phone number {operator_phone} not registered. Contact admin.')

        # If this is a route step QR code, handle dual-scan timing
        if qr_code.route_step:
            job_card = qr_code.route_step.job_card
            scanned_step = qr_code.route_step
            current_status = scanned_step.status

            # Find the expected next step (first PENDING step in sequence)
            expected_step = job_card.route_steps.filter(
                status=models.RouteStepStatus.PENDING
            ).order_by('sequence').first()

            # Validate sequence (for PENDING steps only)
            is_valid_sequence = True
            if current_status == models.RouteStepStatus.PENDING:
                is_valid_sequence = (expected_step and scanned_step.pk == expected_step.pk)

            # Generate unique log number
            from datetime import datetime
            log_count = models.ProcessExecutionLog.objects.filter(
                log_number__startswith=f'LOG-{datetime.now().year}'
            ).count() + 1
            log_number = f'LOG-{datetime.now().year}-{log_count:06d}'

            # DUAL-SCAN LOGIC
            if current_status == models.RouteStepStatus.PENDING:
                # FIRST SCAN: Start the process
                if not is_valid_sequence:
                    # Wrong process scanned - create error log
                    execution_log = models.ProcessExecutionLog.objects.create(
                        log_number=log_number,
                        job_route_step=scanned_step,
                        job_card=job_card,
                        process_code=scanned_step.process_code,
                        operator=operator,
                        operator_name=operator.name if operator else (request.user.username if request.user.is_authenticated else 'Unknown'),
                        was_valid_sequence=False,
                        expected_process_code=expected_step.process_code if expected_step else '',
                        validation_message=f"Wrong process! Expected: {expected_step.process_code if expected_step else 'None'}",
                        department=scanned_step.department,
                        scanned_at=timezone.now()
                    )
                    messages.error(
                        request,
                        f'⚠️ WRONG PROCESS SCANNED!\n\n'
                        f'You scanned: {scanned_step.process_code}\n'
                        f'Expected next step: {expected_step.process_code if expected_step else "None (all steps complete)"}\n\n'
                        f'Please scan the correct QR code or submit a correction request if you already started this process.'
                    )
                    return redirect(
                        f'/production/jobcards/{job_card.pk}/?validation_error=true&log_id={execution_log.pk}'
                    )

                # Valid sequence - START the process
                scanned_step.status = models.RouteStepStatus.IN_PROGRESS
                scanned_step.actual_start = timezone.now()
                scanned_step.operator = operator
                if operator:
                    scanned_step.operator_name = operator.name
                scanned_step.save()

                # Create execution log for start
                execution_log = models.ProcessExecutionLog.objects.create(
                    log_number=log_number,
                    job_route_step=scanned_step,
                    job_card=job_card,
                    process_code=scanned_step.process_code,
                    operator=operator,
                    operator_name=operator.name if operator else (request.user.username if request.user.is_authenticated else 'Unknown'),
                    was_valid_sequence=True,
                    validation_message="Process started",
                    department=scanned_step.department,
                    scanned_at=timezone.now(),
                    started_at=timezone.now()
                )

                operator_name = operator.name if operator else 'Unknown'
                messages.success(
                    request,
                    f'✓ Process STARTED by {operator_name}\n'
                    f'Process: {scanned_step.process_code}\n'
                    f'Scan again when finished to complete.'
                )

            elif current_status == models.RouteStepStatus.IN_PROGRESS:
                # SECOND SCAN: End the process

                # Check if same operator (if operator is known)
                if operator and scanned_step.operator and scanned_step.operator != operator:
                    messages.error(
                        request,
                        f'⚠️ OPERATOR MISMATCH!\n\n'
                        f'This process was started by: {scanned_step.operator.name}\n'
                        f'You are: {operator.name}\n\n'
                        f'Only the operator who started can complete it, or submit a correction request.'
                    )
                    return redirect('production:jobcard-detail', pk=job_card.pk)

                # Complete the process
                scanned_step.status = models.RouteStepStatus.DONE
                scanned_step.actual_end = timezone.now()
                scanned_step.save()

                # Calculate duration
                duration = None
                if scanned_step.actual_start and scanned_step.actual_end:
                    duration = scanned_step.actual_end - scanned_step.actual_start

                # Find and update the execution log
                execution_log = models.ProcessExecutionLog.objects.filter(
                    job_route_step=scanned_step,
                    started_at__isnull=False,
                    completed_at__isnull=True
                ).order_by('-started_at').first()

                if execution_log:
                    execution_log.completed_at = timezone.now()
                    execution_log.validation_message = "Process completed"
                    execution_log.save()

                # Update or create time metric for analytics
                if duration and scanned_step.operator:
                    # Get bit information for metrics
                    bit_instance = job_card.work_order.bit_instance if hasattr(job_card.work_order, 'bit_instance') and job_card.work_order.bit_instance else None

                    models.ProcessTimeMetric.objects.update_or_create(
                        job_route_step=scanned_step,
                        defaults={
                            'job_card': job_card,
                            'process_code': scanned_step.process_code,
                            'department': scanned_step.department,
                            'workstation': scanned_step.workstation,
                            'operator': scanned_step.operator,
                            'bit_type': bit_instance.bit_type if bit_instance else '',
                            'body_material': bit_instance.body_material if bit_instance else '',
                            'bit_size_inch': bit_instance.bit_size_inch if bit_instance else 0,
                            'blade_count': bit_instance.blade_count if bit_instance else 0,
                            'processing_time_minutes': duration.total_seconds() / 60,
                            'total_time_minutes': duration.total_seconds() / 60,
                            'completed_at': timezone.now()
                        }
                    )

                operator_name = scanned_step.operator.name if scanned_step.operator else 'Unknown'
                duration_str = f'{int(duration.total_seconds() / 60)} minutes' if duration else 'N/A'
                messages.success(
                    request,
                    f'✓ Process COMPLETED by {operator_name}\n'
                    f'Process: {scanned_step.process_code}\n'
                    f'Duration: {duration_str}'
                )

            elif current_status == models.RouteStepStatus.DONE:
                # Already completed
                messages.info(
                    request,
                    f'ℹ️ This process is already COMPLETED.\n'
                    f'Process: {scanned_step.process_code}\n'
                    f'Completed by: {scanned_step.operator.name if scanned_step.operator else "Unknown"}'
                )

            return redirect('production:jobcard-detail', pk=job_card.pk)

        # For job card QR codes (not step-specific), just redirect
        elif qr_code.job_card:
            return redirect('production:jobcard-detail', pk=qr_code.job_card.pk)
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


# ============================================================================
# PROCESS CORRECTION REQUESTS
# ============================================================================

class ProcessCorrectionRequestCreateView(LoginRequiredMixin, CreateView):
    """
    Create a correction request for a wrongly executed process
    Operator-initiated workflow requiring supervisor approval
    """
    model = models.ProcessCorrectionRequest
    template_name = 'production/correction_request_form.html'
    fields = [
        'job_route_step', 'correction_type', 'reason',
        'impact_description', 'priority'
    ]

    def get_initial(self):
        initial = super().get_initial()

        # Pre-fill from URL parameters
        step_id = self.request.GET.get('step_id')
        log_id = self.request.GET.get('log_id')

        if step_id:
            initial['job_route_step'] = step_id

        # Auto-generate request number
        from datetime import datetime
        year = datetime.now().year
        count = models.ProcessCorrectionRequest.objects.filter(
            request_number__startswith=f'CORR-{year}'
        ).count() + 1
        self.request_number = f'CORR-{year}-{count:04d}'

        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add execution log if available
        log_id = self.request.GET.get('log_id')
        if log_id:
            try:
                context['execution_log'] = models.ProcessExecutionLog.objects.get(pk=log_id)
            except models.ProcessExecutionLog.DoesNotExist:
                pass

        # Add step details if available
        step_id = self.request.GET.get('step_id')
        if step_id:
            try:
                context['route_step'] = models.JobRouteStep.objects.get(pk=step_id)
            except models.JobRouteStep.DoesNotExist:
                pass

        return context

    def form_valid(self, form):
        # Set request number and metadata
        form.instance.request_number = self.request_number
        form.instance.requested_by_name = self.request.user.username

        # Try to link employee if exists
        try:
            employee = models.Employee.objects.get(user=self.request.user)
            form.instance.requested_by = employee
        except models.Employee.DoesNotExist:
            pass

        # Set job card from route step
        form.instance.job_card = form.instance.job_route_step.job_card

        # Link execution log if provided
        log_id = self.request.GET.get('log_id')
        if log_id:
            try:
                form.instance.execution_log = models.ProcessExecutionLog.objects.get(pk=log_id)
            except models.ProcessExecutionLog.DoesNotExist:
                pass

        # Save original state
        form.instance.original_step_status = form.instance.job_route_step.status
        if form.instance.job_route_step.actual_operator:
            form.instance.original_operator_name = str(form.instance.job_route_step.actual_operator)

        messages.success(
            self.request,
            f'Correction request {form.instance.request_number} submitted. '
            f'A supervisor will review it shortly.'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('production:jobcard-detail',
                          kwargs={'pk': self.object.job_card.pk})


class ProcessCorrectionRequestListView(LoginRequiredMixin, ListView):
    """
    List all correction requests with filtering
    """
    model = models.ProcessCorrectionRequest
    template_name = 'production/correction_request_list.html'
    context_object_name = 'requests'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'job_card', 'job_route_step', 'requested_by',
            'supervisor_reviewed_by'
        )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        else:
            # Show pending requests by default
            queryset = queryset.filter(
                status=models.CorrectionRequestStatus.PENDING
            )

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset.order_by('-requested_at')


class ProcessCorrectionRequestDetailView(LoginRequiredMixin, DetailView):
    """
    Correction request details with approval/rejection actions
    """
    model = models.ProcessCorrectionRequest
    template_name = 'production/correction_request_detail.html'
    context_object_name = 'request'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check if current user can approve
        context['can_approve'] = False
        if self.request.user.is_staff or self.request.user.is_superuser:
            context['can_approve'] = True
        else:
            # Check if user is a supervisor
            try:
                employee = models.Employee.objects.get(user=self.request.user)
                if employee.role in ['SUPERVISOR', 'MANAGER']:
                    context['can_approve'] = True
            except models.Employee.DoesNotExist:
                pass

        return context


def approve_correction_request(request, pk):
    """
    Approve a correction request (supervisor action)
    """
    correction_request = get_object_or_404(models.ProcessCorrectionRequest, pk=pk)

    if request.method == 'POST':
        # Check permission
        if not (request.user.is_staff or request.user.is_superuser):
            try:
                employee = models.Employee.objects.get(user=request.user)
                if employee.role not in ['SUPERVISOR', 'MANAGER']:
                    messages.error(request, 'Only supervisors can approve correction requests.')
                    return redirect('production:correction-request-detail', pk=pk)
            except models.Employee.DoesNotExist:
                messages.error(request, 'Only supervisors can approve correction requests.')
                return redirect('production:correction-request-detail', pk=pk)

        # Get supervisor employee instance
        try:
            supervisor = models.Employee.objects.get(user=request.user)
        except models.Employee.DoesNotExist:
            supervisor = None

        # Get notes from form
        notes = request.POST.get('notes', '')

        # Approve the request
        correction_request.approve(supervisor=supervisor, notes=notes)

        # Execute the correction if auto-execute is enabled
        if request.POST.get('auto_execute') == 'true':
            try:
                correction_request.execute_correction(
                    performed_by=supervisor,
                    notes=f"Auto-executed upon approval. {notes}"
                )
                messages.success(
                    request,
                    f'Correction request {correction_request.request_number} approved and executed. '
                    f'Process step has been reversed.'
                )
            except Exception as e:
                messages.error(
                    request,
                    f'Correction approved but execution failed: {str(e)}'
                )
        else:
            messages.success(
                request,
                f'Correction request {correction_request.request_number} approved. '
                f'Execute the correction manually or from the detail page.'
            )

        return redirect('production:correction-request-detail', pk=pk)

    return redirect('production:correction-request-detail', pk=pk)


def reject_correction_request(request, pk):
    """
    Reject a correction request (supervisor action)
    """
    correction_request = get_object_or_404(models.ProcessCorrectionRequest, pk=pk)

    if request.method == 'POST':
        # Check permission
        if not (request.user.is_staff or request.user.is_superuser):
            try:
                employee = models.Employee.objects.get(user=request.user)
                if employee.role not in ['SUPERVISOR', 'MANAGER']:
                    messages.error(request, 'Only supervisors can reject correction requests.')
                    return redirect('production:correction-request-detail', pk=pk)
            except models.Employee.DoesNotExist:
                messages.error(request, 'Only supervisors can reject correction requests.')
                return redirect('production:correction-request-detail', pk=pk)

        # Get supervisor employee instance
        try:
            supervisor = models.Employee.objects.get(user=request.user)
        except models.Employee.DoesNotExist:
            supervisor = None

        # Get notes from form
        notes = request.POST.get('notes', '')

        # Reject the request
        correction_request.reject(supervisor=supervisor, notes=notes)

        messages.warning(
            request,
            f'Correction request {correction_request.request_number} rejected.'
        )

        return redirect('production:correction-request-detail', pk=pk)

    return redirect('production:correction-request-detail', pk=pk)


def execute_correction_request(request, pk):
    """
    Execute an approved correction request
    """
    correction_request = get_object_or_404(models.ProcessCorrectionRequest, pk=pk)

    if request.method == 'POST':
        # Check if approved
        if correction_request.status != models.CorrectionRequestStatus.APPROVED:
            messages.error(
                request,
                'Can only execute approved correction requests.'
            )
            return redirect('production:correction-request-detail', pk=pk)

        # Get performer
        try:
            performer = models.Employee.objects.get(user=request.user)
        except models.Employee.DoesNotExist:
            performer = None

        # Get notes
        notes = request.POST.get('notes', '')

        # Execute
        try:
            correction_request.execute_correction(
                performed_by=performer,
                notes=notes
            )
            messages.success(
                request,
                f'Correction executed successfully. Process step has been reversed to PENDING status.'
            )
        except Exception as e:
            messages.error(request, f'Failed to execute correction: {str(e)}')

        return redirect('production:correction-request-detail', pk=pk)

    return redirect('production:correction-request-detail', pk=pk)


# ============================================================================
# EXECUTION LOGS
# ============================================================================

class ProcessExecutionLogListView(LoginRequiredMixin, ListView):
    """
    Complete audit trail of all process executions
    """
    model = models.ProcessExecutionLog
    template_name = 'production/execution_log_list.html'
    context_object_name = 'logs'
    paginate_by = 100

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'job_card', 'job_route_step', 'operator', 'correction_request'
        )

        # Filter by job card
        job_card_id = self.request.GET.get('job_card')
        if job_card_id:
            queryset = queryset.filter(job_card_id=job_card_id)

        # Filter by operator
        operator_id = self.request.GET.get('operator')
        if operator_id:
            queryset = queryset.filter(operator_id=operator_id)

        # Filter by validity
        validity = self.request.GET.get('validity')
        if validity == 'valid':
            queryset = queryset.filter(was_valid_sequence=True)
        elif validity == 'invalid':
            queryset = queryset.filter(was_valid_sequence=False)

        # Filter by corrected status
        corrected = self.request.GET.get('corrected')
        if corrected == 'yes':
            queryset = queryset.filter(was_corrected=True)
        elif corrected == 'no':
            queryset = queryset.filter(was_corrected=False)

        return queryset.order_by('-scanned_at')
