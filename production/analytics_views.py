"""
Production Analytics and WIP Dashboard Views
=============================================
Real-time floor status, KPIs, and process analytics
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Count, Avg, Sum, F, ExpressionWrapper, DecimalField, DurationField
from django.db.models.functions import TruncDate, Coalesce
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from . import models


class WIPDashboardView(LoginRequiredMixin, TemplateView):
    """
    Powerful Work-In-Progress Dashboard
    Shows all bits currently on the floor with filtering
    """
    template_name = 'production/wip_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filter parameters
        bit_type_filter = self.request.GET.get('bit_type', '')
        body_material_filter = self.request.GET.get('body_material', '')
        size_filter = self.request.GET.get('size', '')
        department_filter = self.request.GET.get('department', '')
        status_filter = self.request.GET.get('status', '')

        # Base queryset: all bits currently in production or QC
        wip_bits = models.BitInstance.objects.filter(
            status__in=['IN_PRODUCTION', 'IN_REPAIR']
        ).select_related(
            'design_revision__design'
        ).prefetch_related(
            'work_orders__job_cards__route_steps',
            'location_history'
        )

        # Apply filters
        if bit_type_filter:
            wip_bits = wip_bits.filter(design_revision__design__bit_type=bit_type_filter)

        if body_material_filter:
            wip_bits = wip_bits.filter(design_revision__design__body_material=body_material_filter)

        if size_filter:
            wip_bits = wip_bits.filter(design_revision__design__size_inch=Decimal(size_filter))

        # Get active job cards
        active_job_cards = models.JobCard.objects.filter(
            status__in=['RELEASED', 'IN_PROGRESS', 'QC_HOLD']
        ).select_related(
            'work_order__bit_instance__design_revision__design',
            'work_order'
        ).prefetch_related('route_steps')

        if department_filter:
            active_job_cards = active_job_cards.filter(department=department_filter)

        if status_filter:
            active_job_cards = active_job_cards.filter(status=status_filter)

        # Calculate progress for each job card
        job_cards_with_progress = []
        for jc in active_job_cards:
            total_steps = jc.route_steps.count()
            completed_steps = jc.route_steps.filter(status='DONE').count()
            in_progress_steps = jc.route_steps.filter(status='IN_PROGRESS').count()

            progress_pct = (completed_steps / total_steps * 100) if total_steps > 0 else 0

            # Get current step
            current_step = jc.route_steps.filter(
                status='IN_PROGRESS'
            ).order_by('sequence').first()

            if not current_step:
                # Get next pending step
                current_step = jc.route_steps.filter(
                    status='PENDING'
                ).order_by('sequence').first()

            # Get current location
            if jc.work_order.bit_instance:
                latest_location = jc.work_order.bit_instance.location_history.first()
            else:
                latest_location = None

            # Calculate time in current step
            time_in_step = None
            if current_step and current_step.actual_start:
                time_in_step = (timezone.now() - current_step.actual_start).total_seconds() / 3600  # hours

            job_cards_with_progress.append({
                'job_card': jc,
                'total_steps': total_steps,
                'completed_steps': completed_steps,
                'in_progress_steps': in_progress_steps,
                'progress_pct': round(progress_pct, 1),
                'current_step': current_step,
                'latest_location': latest_location,
                'time_in_step_hours': round(time_in_step, 1) if time_in_step else None,
                'bit_instance': jc.work_order.bit_instance,
                'design': jc.work_order.design_revision.design if jc.work_order.design_revision else None
            })

        # Summary statistics
        context['total_wip'] = len(job_cards_with_progress)
        context['by_department'] = active_job_cards.values('department').annotate(
            count=Count('id')
        ).order_by('-count')
        context['by_status'] = active_job_cards.values('status').annotate(
            count=Count('id')
        ).order_by('-count')

        # Bits by type/size
        if bit_type_filter:
            context['by_bit_type'] = [{'bit_type': bit_type_filter, 'count': len(job_cards_with_progress)}]
        else:
            # Count by bit type
            bit_type_counts = {}
            for item in job_cards_with_progress:
                if item['design']:
                    bt = item['design'].bit_type
                    bit_type_counts[bt] = bit_type_counts.get(bt, 0) + 1
            context['by_bit_type'] = [
                {'bit_type': k, 'count': v} for k, v in bit_type_counts.items()
            ]

        # Available filter options
        context['bit_types'] = models.BitType.choices
        context['body_materials'] = models.BodyMaterial.choices
        context['departments'] = models.Department.choices
        context['statuses'] = models.JobCardStatus.choices

        # Unique sizes in system
        context['available_sizes'] = models.BitDesign.objects.values_list(
            'size_inch', flat=True
        ).distinct().order_by('size_inch')

        context['job_cards_with_progress'] = job_cards_with_progress

        # Current filters
        context['current_filters'] = {
            'bit_type': bit_type_filter,
            'body_material': body_material_filter,
            'size': size_filter,
            'department': department_filter,
            'status': status_filter
        }

        return context


class ProcessAnalyticsView(LoginRequiredMixin, TemplateView):
    """
    Process time analytics and averages
    """
    template_name = 'production/process_analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get filter parameters
        process_filter = self.request.GET.get('process', '')
        bit_type_filter = self.request.GET.get('bit_type', '')
        days_back = int(self.request.GET.get('days', 30))

        # Date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)

        # Get process time metrics
        metrics = models.ProcessTimeMetric.objects.filter(
            completed_at__gte=start_date
        )

        if process_filter:
            metrics = metrics.filter(process_code=process_filter)

        if bit_type_filter:
            metrics = metrics.filter(bit_type=bit_type_filter)

        # Calculate averages by process
        process_averages = metrics.values('process_code').annotate(
            avg_processing=Avg('processing_time_minutes'),
            avg_wait=Avg('wait_time_before_minutes'),
            avg_total=Avg('total_time_minutes'),
            count=Count('id')
        ).order_by('process_code')

        # Calculate averages by process and bit size
        size_averages = metrics.values(
            'process_code', 'bit_type', 'bit_size_inch'
        ).annotate(
            avg_processing=Avg('processing_time_minutes'),
            avg_wait=Avg('wait_time_before_minutes'),
            avg_setup=Avg('setup_time_minutes'),
            count=Count('id')
        ).order_by('process_code', 'bit_size_inch')

        # Identify delays (wait time > avg * 1.5)
        avg_wait_overall = metrics.aggregate(Avg('wait_time_before_minutes'))['wait_time_before_minutes__avg'] or 0
        threshold = avg_wait_overall * 1.5

        delays = metrics.filter(
            wait_time_before_minutes__gt=threshold
        ).select_related('job_card', 'operator').order_by('-wait_time_before_minutes')[:20]

        # Department efficiency
        dept_stats = metrics.values('department').annotate(
            total_processing=Sum('processing_time_minutes'),
            total_wait=Sum('wait_time_before_minutes'),
            count=Count('id')
        ).order_by('department')

        for dept in dept_stats:
            total = dept['total_processing'] + dept['total_wait']
            if total > 0:
                dept['efficiency'] = round((dept['total_processing'] / total) * 100, 1)
            else:
                dept['efficiency'] = 0

        # Operator performance
        operator_stats = metrics.filter(
            operator__isnull=False
        ).values('operator__employee_code', 'operator__first_name', 'operator__last_name').annotate(
            avg_time=Avg('processing_time_minutes'),
            count=Count('id')
        ).order_by('avg_time')[:10]

        context['process_averages'] = process_averages
        context['size_averages'] = size_averages
        context['delays'] = delays
        context['dept_stats'] = dept_stats
        context['operator_stats'] = operator_stats
        context['avg_wait_threshold'] = round(threshold, 1)
        context['days_back'] = days_back

        # Available processes
        context['available_processes'] = models.ProcessTimeMetric.objects.values_list(
            'process_code', flat=True
        ).distinct().order_by('process_code')

        return context


class KPIDashboardView(LoginRequiredMixin, TemplateView):
    """
    KPI Dashboard showing department performance
    """
    template_name = 'production/kpi_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Date range
        days_back = int(self.request.GET.get('days', 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days_back)

        # Get KPIs
        kpis = models.DepartmentKPI.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-date', 'department')

        # Summary by department
        dept_summary = kpis.values('department').annotate(
            avg_efficiency=Avg('efficiency_percentage'),
            total_completed=Sum('jobs_completed'),
            total_downtime=Sum('total_downtime_hours'),
            avg_delay=Avg('avg_delay_minutes')
        ).order_by('-avg_efficiency')

        # Trend data for charts (last 7 days by department)
        trend_data = {}
        for dept_choice in models.Department.choices:
            dept_code = dept_choice[0]
            dept_kpis = kpis.filter(department=dept_code).order_by('date')
            trend_data[dept_code] = {
                'dates': [k.date.strftime('%Y-%m-%d') for k in dept_kpis],
                'efficiency': [float(k.efficiency_percentage) for k in dept_kpis],
                'completed': [k.jobs_completed for k in dept_kpis]
            }

        context['kpis'] = kpis
        context['dept_summary'] = dept_summary
        context['trend_data'] = trend_data
        context['days_back'] = days_back

        return context


class MaintenanceRequestCreateView(LoginRequiredMixin, CreateView):
    """
    Create maintenance request for equipment
    """
    model = models.MaintenanceRequest
    template_name = 'production/maintenance_request_form.html'
    fields = [
        'request_number', 'equipment', 'request_type', 'priority',
        'reported_by', 'reported_by_name', 'problem_description',
        'impact_on_production'
    ]

    def get_initial(self):
        initial = super().get_initial()
        # Auto-generate request number
        from datetime import datetime
        year = datetime.now().year
        count = models.MaintenanceRequest.objects.filter(
            request_number__startswith=f'MAINT-{year}'
        ).count() + 1
        initial['request_number'] = f'MAINT-{year}-{count:03d}'
        return initial

    def form_valid(self, form):
        # Set downtime if critical
        if form.instance.priority == 'CRITICAL':
            form.instance.downtime_start = timezone.now()
            form.instance.equipment.status = 'BREAKDOWN'
            form.instance.equipment.save()

        messages.success(
            self.request,
            f'Maintenance request {form.instance.request_number} created. '
            f'Priority: {form.instance.get_priority_display()}'
        )
        return super().form_valid(form)

    def get_success_url(self):
        from django.urls import reverse_lazy
        return reverse_lazy('production:maintenance-list')


class MaintenanceRequestListView(LoginRequiredMixin, ListView):
    """
    List all maintenance requests with filtering
    """
    model = models.MaintenanceRequest
    template_name = 'production/maintenance_request_list.html'
    context_object_name = 'requests'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset().select_related('equipment', 'reported_by', 'assigned_to')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        else:
            # Show active requests by default
            queryset = queryset.exclude(status__in=['COMPLETED', 'CANCELLED'])

        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by equipment
        equipment_id = self.request.GET.get('equipment')
        if equipment_id:
            queryset = queryset.filter(equipment_id=equipment_id)

        return queryset.order_by('-priority', '-reported_at')


class EquipmentListView(LoginRequiredMixin, ListView):
    """
    List all equipment with status
    """
    model = models.Equipment
    template_name = 'production/equipment_list.html'
    context_object_name = 'equipment_list'
    paginate_by = 50

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department=department)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset.order_by('department', 'equipment_code')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Summary statistics
        context['total_equipment'] = models.Equipment.objects.count()
        context['operational'] = models.Equipment.objects.filter(status='OPERATIONAL').count()
        context['under_maintenance'] = models.Equipment.objects.filter(status='MAINTENANCE').count()
        context['broken_down'] = models.Equipment.objects.filter(status='BREAKDOWN').count()
        context['maintenance_due'] = models.Equipment.objects.filter(
            next_maintenance_date__lte=timezone.now().date()
        ).count()

        return context
