"""
HR Portal Views - Version C
Employee self-service portal views.

All views in this file are for regular employees, not HR staff.
HR back-office views are in hr/views.py.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from hr.models import (
    HREmployee, LeaveRequest, LeaveType,
    AttendanceRecord, EmployeeTraining,
    EmployeeDocument, AssetAssignment,
)
from .models import EmployeeRequest


# ============================================================================
# HELPER MIXIN
# ============================================================================

class EmployeeRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure user has an associated employee record."""

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'hr_employee'):
            messages.error(request, 'You must be an employee to access this portal.')
            return redirect('admin:index')  # Or some other appropriate page
        return super().dispatch(request, *args, **kwargs)

    def get_employee(self):
        """Get the current logged-in user's employee record."""
        return self.request.user.hr_employee


# ============================================================================
# DASHBOARD
# ============================================================================

class PortalDashboardView(EmployeeRequiredMixin, TemplateView):
    """Employee portal dashboard - shows personalized overview."""
    template_name = 'hr_portal/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_employee()

        # My upcoming leaves
        today = timezone.now().date()
        context['upcoming_leaves'] = LeaveRequest.objects.filter(
            employee=employee,
            status__in=['APPROVED', 'PENDING'],
            start_date__gte=today
        ).order_by('start_date')[:5]

        # My pending requests
        context['pending_requests'] = EmployeeRequest.objects.filter(
            employee=employee,
            status='SUBMITTED'
        ).count()

        # Recent attendance (last 7 days)
        seven_days_ago = today - timedelta(days=7)
        context['recent_attendance'] = AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=seven_days_ago
        ).order_by('-date')

        # My training sessions (upcoming)
        context['upcoming_training'] = EmployeeTraining.objects.filter(
            employee=employee,
            session__session_date__gte=today,
            session__status='SCHEDULED'
        ).select_related('session__program').order_by('session__session_date')[:5]

        # My assigned assets
        context['my_assets'] = AssetAssignment.objects.filter(
            employee=employee,
            returned_date__isnull=True
        ).select_related('asset__asset_type')[:5]

        return context


# ============================================================================
# MY PROFILE
# ============================================================================

class MyProfileView(EmployeeRequiredMixin, TemplateView):
    """View my profile - read-only for employees."""
    template_name = 'hr_portal/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.get_employee()

        context['employee'] = employee
        context['person'] = employee.person
        context['current_contract'] = employee.contracts.filter(is_active=True).first()
        context['qualifications'] = employee.qualifications.select_related('qualification_level').all()
        context['phones'] = employee.person.phones.all()
        context['emails'] = employee.person.emails.all()

        # Calculate employment duration
        if employee.hire_date:
            duration = timezone.now().date() - employee.hire_date
            years = duration.days // 365
            months = (duration.days % 365) // 30
            context['employment_duration'] = {
                'years': years,
                'months': months
            }

        # TODO-QR: Display employee badge QR code here
        # context['badge_qr_code'] = employee.person.badge_qr_code

        return context


# ============================================================================
# MY LEAVES
# ============================================================================

class MyLeaveListView(EmployeeRequiredMixin, ListView):
    """List my leave requests."""
    model = LeaveRequest
    template_name = 'hr_portal/leaves/list.html'
    context_object_name = 'leave_requests'
    paginate_by = 20

    def get_queryset(self):
        employee = self.get_employee()
        return LeaveRequest.objects.filter(
            employee=employee
        ).select_related('leave_type', 'approved_by').order_by('-start_date')


class MyLeaveDetailView(EmployeeRequiredMixin, DetailView):
    """View my leave request details."""
    model = LeaveRequest
    template_name = 'hr_portal/leaves/detail.html'
    context_object_name = 'leave_request'

    def get_queryset(self):
        """Only allow viewing own leave requests."""
        employee = self.get_employee()
        return LeaveRequest.objects.filter(employee=employee)


class MyLeaveCreateView(EmployeeRequiredMixin, CreateView):
    """Submit a new leave request."""
    model = LeaveRequest
    template_name = 'hr_portal/leaves/form.html'
    fields = ['leave_type', 'start_date', 'end_date', 'reason']
    success_url = reverse_lazy('hr_portal:my_leaves')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Show available leave types
        context['leave_types'] = LeaveType.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        employee = self.get_employee()
        form.instance.employee = employee

        # Calculate days count
        delta = form.instance.end_date - form.instance.start_date
        form.instance.days_count = delta.days + 1

        # Set initial status based on leave type
        if form.instance.leave_type.requires_approval:
            form.instance.status = 'PENDING'
        else:
            form.instance.status = 'APPROVED'

        messages.success(
            self.request,
            f'Leave request submitted successfully. Status: {form.instance.status}'
        )

        # TODO-QR: Send notification to manager/HR
        # from core_foundation.models import Notification
        # Notification.create(
        #     user=employee.department.manager.user,
        #     title='New Leave Request',
        #     message=f'{employee.person.full_name_en} has requested leave.'
        # )

        return super().form_valid(form)


# ============================================================================
# MY GENERAL REQUESTS
# ============================================================================

class MyRequestListView(EmployeeRequiredMixin, ListView):
    """List my general requests (certificates, letters, etc.)."""
    model = EmployeeRequest
    template_name = 'hr_portal/requests/list.html'
    context_object_name = 'requests'
    paginate_by = 20

    def get_queryset(self):
        employee = self.get_employee()
        return EmployeeRequest.objects.filter(
            employee=employee
        ).order_by('-created_at')


class MyRequestDetailView(EmployeeRequiredMixin, DetailView):
    """View my request details."""
    model = EmployeeRequest
    template_name = 'hr_portal/requests/detail.html'
    context_object_name = 'request'

    def get_queryset(self):
        """Only allow viewing own requests."""
        employee = self.get_employee()
        return EmployeeRequest.objects.filter(employee=employee)


class MyRequestCreateView(EmployeeRequiredMixin, CreateView):
    """Submit a new general request."""
    model = EmployeeRequest
    template_name = 'hr_portal/requests/form.html'
    fields = ['request_type', 'title', 'description']
    success_url = reverse_lazy('hr_portal:my_requests')

    def form_valid(self, form):
        employee = self.get_employee()
        form.instance.employee = employee
        form.instance.status = 'SUBMITTED'

        messages.success(self.request, 'Request submitted successfully. HR will review it soon.')

        # TODO-QR: Send notification to HR
        # from core_foundation.models import Notification
        # Notification.create(
        #     to_group='HR',
        #     title='New Employee Request',
        #     message=f'{employee.person.full_name_en} submitted a {form.instance.get_request_type_display()} request.'
        # )

        return super().form_valid(form)


# ============================================================================
# MY ATTENDANCE
# ============================================================================

class MyAttendanceView(EmployeeRequiredMixin, ListView):
    """View my attendance records - read-only."""
    model = AttendanceRecord
    template_name = 'hr_portal/attendance.html'
    context_object_name = 'attendance_records'
    paginate_by = 30

    def get_queryset(self):
        employee = self.get_employee()
        # Default: last 30 days
        days = int(self.request.GET.get('days', 30))
        start_date = timezone.now().date() - timedelta(days=days)

        return AttendanceRecord.objects.filter(
            employee=employee,
            date__gte=start_date
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate summary stats
        records = self.get_queryset()
        context['total_days'] = records.count()
        context['present_days'] = records.filter(status='PRESENT').count()
        context['late_days'] = records.filter(late_minutes__gt=0).count()
        context['total_late_minutes'] = sum(r.late_minutes for r in records)
        context['total_overtime_minutes'] = sum(r.overtime_minutes for r in records)

        return context


# ============================================================================
# MY TRAINING
# ============================================================================

class MyTrainingView(EmployeeRequiredMixin, ListView):
    """View my training records."""
    model = EmployeeTraining
    template_name = 'hr_portal/training.html'
    context_object_name = 'training_records'
    paginate_by = 20

    def get_queryset(self):
        employee = self.get_employee()
        return EmployeeTraining.objects.filter(
            employee=employee
        ).select_related('session__program').order_by('-session__session_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Upcoming training sessions
        today = timezone.now().date()
        context['upcoming_sessions'] = self.get_queryset().filter(
            session__session_date__gte=today,
            session__status='SCHEDULED'
        )

        # Completed training
        context['completed_count'] = self.get_queryset().filter(
            attended=True,
            passed=True
        ).count()

        return context


# ============================================================================
# MY DOCUMENTS
# ============================================================================

class MyDocumentsView(EmployeeRequiredMixin, ListView):
    """View my documents."""
    model = EmployeeDocument
    template_name = 'hr_portal/documents.html'
    context_object_name = 'documents'

    def get_queryset(self):
        employee = self.get_employee()
        return EmployeeDocument.objects.filter(
            employee=employee
        ).select_related('document_type').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Check for expiring documents
        today = timezone.now().date()
        threshold = today + timedelta(days=30)

        context['expiring_soon'] = self.get_queryset().filter(
            expiry_date__lte=threshold,
            expiry_date__gte=today
        )

        context['expired'] = self.get_queryset().filter(
            expiry_date__lt=today
        )

        return context


# ============================================================================
# MY ASSETS
# ============================================================================

class MyAssetsView(EmployeeRequiredMixin, ListView):
    """View assets assigned to me."""
    model = AssetAssignment
    template_name = 'hr_portal/assets.html'
    context_object_name = 'asset_assignments'

    def get_queryset(self):
        employee = self.get_employee()
        return AssetAssignment.objects.filter(
            employee=employee
        ).select_related('asset__asset_type').order_by('-assigned_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Current assets (not returned)
        context['current_assets'] = self.get_queryset().filter(returned_date__isnull=True)

        # Returned assets (history)
        context['returned_assets'] = self.get_queryset().filter(returned_date__isnull=False)

        # TODO-QR: Add QR codes for each asset
        # for asset in context['current_assets']:
        #     asset.qr_code_url = generate_qr_code(asset.asset.asset_number)

        return context
