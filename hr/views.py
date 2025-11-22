"""
HR Back-Office Views - Version C
Views for HR administration and back-office functionality.

All views in this file are for HR staff use only.
Employee self-service views are in hr_portal/views.py.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, TemplateView, View
)
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse

from .models import (
    HRPerson, HREmployee, Department, Position,
    HRContract, HRShiftTemplate,
    LeaveType, LeaveRequest,
    AttendanceRecord,
    TrainingProgram, TrainingSession, EmployeeTraining,
    DocumentType, EmployeeDocument,
    QualificationLevel, EmployeeQualification,
    AssetType, HRAsset, AssetAssignment,
    HRPhone, HREmail,
)


# ============================================================================
# DASHBOARD
# ============================================================================

class HRDashboardView(LoginRequiredMixin, TemplateView):
    """HR Dashboard showing key metrics and quick links."""
    template_name = 'hr/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Employee statistics
        context['total_employees'] = HREmployee.objects.filter(status='ACTIVE').count()
        context['on_probation'] = HREmployee.objects.filter(status='ON_PROBATION').count()
        context['on_leave'] = HREmployee.objects.filter(status='ON_LEAVE').count()

        # Leave requests pending approval
        context['pending_leaves'] = LeaveRequest.objects.filter(status='PENDING').count()

        # Recent leave requests
        context['recent_leaves'] = LeaveRequest.objects.select_related(
            'employee__person', 'leave_type'
        ).order_by('-created_at')[:10]

        # Today's attendance stats
        today = timezone.now().date()
        context['today_attendance'] = AttendanceRecord.objects.filter(date=today).count()
        context['today_late'] = AttendanceRecord.objects.filter(
            date=today, late_minutes__gt=0
        ).count()

        return context


# ============================================================================
# PERSON MANAGEMENT
# ============================================================================

class PersonListView(LoginRequiredMixin, ListView):
    """List all people (identity records)."""
    model = HRPerson
    template_name = 'hr/people/list.html'
    context_object_name = 'people'
    paginate_by = 50

    def get_queryset(self):
        queryset = HRPerson.objects.all().order_by('-created_at')

        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(first_name_en__icontains=search) |
                Q(last_name_en__icontains=search) |
                Q(national_id__icontains=search) |
                Q(iqama_number__icontains=search)
            )

        return queryset


class PersonDetailView(LoginRequiredMixin, DetailView):
    """View person details."""
    model = HRPerson
    template_name = 'hr/people/detail.html'
    context_object_name = 'person'


class PersonCreateView(LoginRequiredMixin, CreateView):
    """Create a new person record."""
    model = HRPerson
    template_name = 'hr/people/form.html'
    fields = [
        'first_name_en', 'middle_name_en', 'last_name_en',
        'first_name_ar', 'middle_name_ar', 'last_name_ar',
        'national_id', 'iqama_number', 'iqama_expiry',
        'date_of_birth', 'gender', 'nationality_iso2', 'marital_status',
        'photo',
    ]
    success_url = reverse_lazy('hr:person_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Person record created successfully.')
        return super().form_valid(form)


class PersonUpdateView(LoginRequiredMixin, UpdateView):
    """Update person record."""
    model = HRPerson
    template_name = 'hr/people/form.html'
    fields = [
        'first_name_en', 'middle_name_en', 'last_name_en',
        'first_name_ar', 'middle_name_ar', 'last_name_ar',
        'national_id', 'iqama_number', 'iqama_expiry',
        'date_of_birth', 'gender', 'nationality_iso2', 'marital_status',
        'photo',
    ]

    def get_success_url(self):
        return reverse('hr:person_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Person record updated successfully.')
        return super().form_valid(form)


# ============================================================================
# EMPLOYEE MANAGEMENT
# ============================================================================

class EmployeeListView(LoginRequiredMixin, ListView):
    """List all employees."""
    model = HREmployee
    template_name = 'hr/employees/list.html'
    context_object_name = 'employees'
    paginate_by = 50

    def get_queryset(self):
        queryset = HREmployee.objects.select_related(
            'person', 'department', 'position'
        ).order_by('employee_no')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by department
        department = self.request.GET.get('department')
        if department:
            queryset = queryset.filter(department_id=department)

        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(employee_no__icontains=search) |
                Q(person__first_name_en__icontains=search) |
                Q(person__last_name_en__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.filter(is_active=True)
        return context


class EmployeeDetailView(LoginRequiredMixin, DetailView):
    """View employee details."""
    model = HREmployee
    template_name = 'hr/employees/detail.html'
    context_object_name = 'employee'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.object

        # Get related data
        context['contracts'] = employee.contracts.all().order_by('-start_date')
        context['leave_requests'] = employee.leave_requests.all().order_by('-start_date')[:10]
        context['training_records'] = employee.training_records.select_related(
            'session__program'
        ).order_by('-session__session_date')[:10]
        context['documents'] = employee.documents.select_related('document_type').all()
        context['qualifications'] = employee.qualifications.select_related('qualification_level').all()
        context['asset_assignments'] = employee.asset_assignments.select_related(
            'asset__asset_type'
        ).filter(returned_date__isnull=True)

        # Recent attendance (last 30 days)
        from datetime import timedelta
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        context['recent_attendance'] = employee.attendance_records.filter(
            date__gte=thirty_days_ago
        ).order_by('-date')[:30]

        return context


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    """Create a new employee."""
    model = HREmployee
    template_name = 'hr/employees/form.html'
    fields = [
        'person', 'user', 'employee_no',
        'department', 'position', 'status',
        'hire_date', 'probation_end_date',
        'cost_center',
    ]
    success_url = reverse_lazy('hr:employee_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Employee created successfully.')
        return super().form_valid(form)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    """Update employee record."""
    model = HREmployee
    template_name = 'hr/employees/form.html'
    fields = [
        'person', 'user', 'employee_no',
        'department', 'position', 'status',
        'hire_date', 'probation_end_date', 'termination_date',
        'cost_center',
    ]

    def get_success_url(self):
        return reverse('hr:employee_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Employee updated successfully.')
        return super().form_valid(form)


# ============================================================================
# DEPARTMENT MANAGEMENT
# ============================================================================

class DepartmentListView(LoginRequiredMixin, ListView):
    """List all departments."""
    model = Department
    template_name = 'hr/departments/list.html'
    context_object_name = 'departments'

    def get_queryset(self):
        return Department.objects.select_related('parent', 'cost_center').annotate(
            employee_count=Count('employees')
        ).order_by('code')


class DepartmentDetailView(LoginRequiredMixin, DetailView):
    """View department details."""
    model = Department
    template_name = 'hr/departments/detail.html'
    context_object_name = 'department'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = self.object.employees.select_related('person', 'position')
        context['sub_departments'] = self.object.sub_departments.all()
        return context


class DepartmentCreateView(LoginRequiredMixin, CreateView):
    """Create a new department."""
    model = Department
    template_name = 'hr/departments/form.html'
    fields = ['code', 'name', 'parent', 'cost_center', 'is_active']
    success_url = reverse_lazy('hr:department_list')

    def form_valid(self, form):
        messages.success(self.request, 'Department created successfully.')
        return super().form_valid(form)


class DepartmentUpdateView(LoginRequiredMixin, UpdateView):
    """Update department."""
    model = Department
    template_name = 'hr/departments/form.html'
    fields = ['code', 'name', 'parent', 'cost_center', 'is_active']

    def get_success_url(self):
        return reverse('hr:department_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Department updated successfully.')
        return super().form_valid(form)


# ============================================================================
# POSITION MANAGEMENT
# ============================================================================

class PositionListView(LoginRequiredMixin, ListView):
    """List all positions."""
    model = Position
    template_name = 'hr/positions/list.html'
    context_object_name = 'positions'

    def get_queryset(self):
        return Position.objects.annotate(
            employee_count=Count('employees')
        ).order_by('code')


class PositionDetailView(LoginRequiredMixin, DetailView):
    """View position details."""
    model = Position
    template_name = 'hr/positions/detail.html'
    context_object_name = 'position'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['employees'] = self.object.employees.select_related('person', 'department')
        return context


class PositionCreateView(LoginRequiredMixin, CreateView):
    """Create a new position."""
    model = Position
    template_name = 'hr/positions/form.html'
    fields = ['code', 'title', 'category', 'grade_level', 'is_supervisory', 'is_active']
    success_url = reverse_lazy('hr:position_list')

    def form_valid(self, form):
        messages.success(self.request, 'Position created successfully.')
        return super().form_valid(form)


class PositionUpdateView(LoginRequiredMixin, UpdateView):
    """Update position."""
    model = Position
    template_name = 'hr/positions/form.html'
    fields = ['code', 'title', 'category', 'grade_level', 'is_supervisory', 'is_active']

    def get_success_url(self):
        return reverse('hr:position_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Position updated successfully.')
        return super().form_valid(form)


# ============================================================================
# CONTRACT MANAGEMENT
# ============================================================================

class ContractListView(LoginRequiredMixin, ListView):
    """List all contracts."""
    model = HRContract
    template_name = 'hr/contracts/list.html'
    context_object_name = 'contracts'
    paginate_by = 50

    def get_queryset(self):
        queryset = HRContract.objects.select_related(
            'employee__person', 'currency'
        ).order_by('-start_date')

        # Filter by active status
        active = self.request.GET.get('active')
        if active == '1':
            queryset = queryset.filter(is_active=True)

        return queryset


class ContractDetailView(LoginRequiredMixin, DetailView):
    """View contract details."""
    model = HRContract
    template_name = 'hr/contracts/detail.html'
    context_object_name = 'contract'


class ContractCreateView(LoginRequiredMixin, CreateView):
    """Create a new contract."""
    model = HRContract
    template_name = 'hr/contracts/form.html'
    fields = [
        'employee', 'contract_number', 'contract_type',
        'start_date', 'end_date',
        'base_salary', 'currency', 'allowances',
        'working_hours_per_week', 'shift_pattern',
        'notes', 'is_active',
    ]
    success_url = reverse_lazy('hr:contract_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Contract created successfully.')
        return super().form_valid(form)


class ContractUpdateView(LoginRequiredMixin, UpdateView):
    """Update contract."""
    model = HRContract
    template_name = 'hr/contracts/form.html'
    fields = [
        'employee', 'contract_number', 'contract_type',
        'start_date', 'end_date',
        'base_salary', 'currency', 'allowances',
        'working_hours_per_week', 'shift_pattern',
        'notes', 'is_active',
    ]

    def get_success_url(self):
        return reverse('hr:contract_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Contract updated successfully.')
        return super().form_valid(form)


# ============================================================================
# LEAVE MANAGEMENT
# ============================================================================

class LeaveRequestListView(LoginRequiredMixin, ListView):
    """List all leave requests."""
    model = LeaveRequest
    template_name = 'hr/leaves/list.html'
    context_object_name = 'leave_requests'
    paginate_by = 50

    def get_queryset(self):
        queryset = LeaveRequest.objects.select_related(
            'employee__person', 'leave_type', 'approved_by'
        ).order_by('-start_date')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset


class LeaveRequestDetailView(LoginRequiredMixin, DetailView):
    """View leave request details."""
    model = LeaveRequest
    template_name = 'hr/leaves/detail.html'
    context_object_name = 'leave_request'


class LeaveApproveView(LoginRequiredMixin, View):
    """Approve a leave request."""

    def post(self, request, pk):
        leave_request = get_object_or_404(LeaveRequest, pk=pk)

        if leave_request.status != 'PENDING':
            messages.error(request, 'This leave request has already been processed.')
            return redirect('hr:leave_detail', pk=pk)

        leave_request.approve(request.user)
        messages.success(request, 'Leave request approved successfully.')

        # TODO-QR: Send notification to employee
        # from core_foundation.models import Notification
        # Notification.create(
        #     user=leave_request.employee.user,
        #     title='Leave Request Approved',
        #     message=f'Your leave request from {leave_request.start_date} has been approved.'
        # )

        return redirect('hr:leave_detail', pk=pk)


class LeaveRejectView(LoginRequiredMixin, View):
    """Reject a leave request."""

    def post(self, request, pk):
        leave_request = get_object_or_404(LeaveRequest, pk=pk)

        if leave_request.status != 'PENDING':
            messages.error(request, 'This leave request has already been processed.')
            return redirect('hr:leave_detail', pk=pk)

        leave_request.reject(request.user)
        messages.warning(request, 'Leave request rejected.')

        # TODO-QR: Send notification to employee

        return redirect('hr:leave_detail', pk=pk)


class LeaveTypeListView(LoginRequiredMixin, ListView):
    """List all leave types."""
    model = LeaveType
    template_name = 'hr/leave_types/list.html'
    context_object_name = 'leave_types'


class LeaveTypeCreateView(LoginRequiredMixin, CreateView):
    """Create a new leave type."""
    model = LeaveType
    template_name = 'hr/leave_types/form.html'
    fields = [
        'code', 'name', 'description',
        'is_paid', 'requires_approval',
        'max_days_per_year', 'min_days_notice',
        'is_active',
    ]
    success_url = reverse_lazy('hr:leavetype_list')

    def form_valid(self, form):
        messages.success(self.request, 'Leave type created successfully.')
        return super().form_valid(form)


class LeaveTypeUpdateView(LoginRequiredMixin, UpdateView):
    """Update leave type."""
    model = LeaveType
    template_name = 'hr/leave_types/form.html'
    fields = [
        'code', 'name', 'description',
        'is_paid', 'requires_approval',
        'max_days_per_year', 'min_days_notice',
        'is_active',
    ]
    success_url = reverse_lazy('hr:leavetype_list')

    def form_valid(self, form):
        messages.success(self.request, 'Leave type updated successfully.')
        return super().form_valid(form)


# ============================================================================
# ATTENDANCE MANAGEMENT
# ============================================================================

class AttendanceListView(LoginRequiredMixin, ListView):
    """List attendance records."""
    model = AttendanceRecord
    template_name = 'hr/attendance/list.html'
    context_object_name = 'attendance_records'
    paginate_by = 100

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related(
            'employee__person'
        ).order_by('-date', 'employee__employee_no')

        # Filter by date
        date = self.request.GET.get('date')
        if date:
            queryset = queryset.filter(date=date)
        else:
            # Default to today
            queryset = queryset.filter(date=timezone.now().date())

        return queryset


class AttendanceDetailView(LoginRequiredMixin, DetailView):
    """View attendance record details."""
    model = AttendanceRecord
    template_name = 'hr/attendance/detail.html'
    context_object_name = 'attendance'


class AttendanceCreateView(LoginRequiredMixin, CreateView):
    """Create attendance record."""
    model = AttendanceRecord
    template_name = 'hr/attendance/form.html'
    fields = [
        'employee', 'date', 'check_in', 'check_out',
        'status', 'late_minutes', 'overtime_minutes',
        'source', 'notes',
    ]
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'Attendance record created successfully.')
        return super().form_valid(form)


class AttendanceUpdateView(LoginRequiredMixin, UpdateView):
    """Update attendance record."""
    model = AttendanceRecord
    template_name = 'hr/attendance/form.html'
    fields = [
        'employee', 'date', 'check_in', 'check_out',
        'status', 'late_minutes', 'overtime_minutes',
        'source', 'notes',
    ]
    success_url = reverse_lazy('hr:attendance_list')

    def form_valid(self, form):
        messages.success(self.request, 'Attendance record updated successfully.')
        return super().form_valid(form)


class AttendanceImportView(LoginRequiredMixin, TemplateView):
    """Import attendance records from file or WhatsApp."""
    template_name = 'hr/attendance/import.html'

    # TODO: Implement file/WhatsApp import logic
    # This is a placeholder for Phase 2C


# ============================================================================
# TRAINING MANAGEMENT
# ============================================================================

class TrainingProgramListView(LoginRequiredMixin, ListView):
    """List all training programs."""
    model = TrainingProgram
    template_name = 'hr/training/programs/list.html'
    context_object_name = 'programs'


class TrainingProgramDetailView(LoginRequiredMixin, DetailView):
    """View training program details."""
    model = TrainingProgram
    template_name = 'hr/training/programs/detail.html'
    context_object_name = 'program'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.object.sessions.all().order_by('-session_date')
        return context


class TrainingProgramCreateView(LoginRequiredMixin, CreateView):
    """Create a new training program."""
    model = TrainingProgram
    template_name = 'hr/training/programs/form.html'
    fields = [
        'code', 'title', 'description', 'category',
        'duration_hours', 'is_mandatory', 'is_active',
    ]
    success_url = reverse_lazy('hr:training_program_list')

    def form_valid(self, form):
        messages.success(self.request, 'Training program created successfully.')
        return super().form_valid(form)


class TrainingSessionListView(LoginRequiredMixin, ListView):
    """List all training sessions."""
    model = TrainingSession
    template_name = 'hr/training/sessions/list.html'
    context_object_name = 'sessions'

    def get_queryset(self):
        return TrainingSession.objects.select_related('program').order_by('-session_date')


class TrainingSessionDetailView(LoginRequiredMixin, DetailView):
    """View training session details."""
    model = TrainingSession
    template_name = 'hr/training/sessions/detail.html'
    context_object_name = 'session'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendees'] = self.object.attendees.select_related('employee__person')
        return context


class TrainingSessionCreateView(LoginRequiredMixin, CreateView):
    """Create a new training session."""
    model = TrainingSession
    template_name = 'hr/training/sessions/form.html'
    fields = [
        'program', 'session_date', 'start_time', 'end_time',
        'location', 'trainer', 'max_participants', 'status',
    ]
    success_url = reverse_lazy('hr:training_session_list')

    def form_valid(self, form):
        messages.success(self.request, 'Training session created successfully.')
        return super().form_valid(form)


# ============================================================================
# QUALIFICATIONS
# ============================================================================

class QualificationListView(LoginRequiredMixin, ListView):
    """List employee qualifications."""
    model = EmployeeQualification
    template_name = 'hr/qualifications/list.html'
    context_object_name = 'qualifications'
    paginate_by = 50

    def get_queryset(self):
        return EmployeeQualification.objects.select_related(
            'employee__person', 'qualification_level'
        ).order_by('-completion_date')


# ============================================================================
# DOCUMENTS
# ============================================================================

class DocumentListView(LoginRequiredMixin, ListView):
    """List employee documents."""
    model = EmployeeDocument
    template_name = 'hr/documents/list.html'
    context_object_name = 'documents'
    paginate_by = 50

    def get_queryset(self):
        queryset = EmployeeDocument.objects.select_related(
            'employee__person', 'document_type'
        ).order_by('-created_at')

        # Filter by expiring soon
        expiring_soon = self.request.GET.get('expiring_soon')
        if expiring_soon:
            from datetime import timedelta
            threshold = timezone.now().date() + timedelta(days=30)
            queryset = queryset.filter(
                expiry_date__lte=threshold,
                expiry_date__gte=timezone.now().date()
            )

        return queryset


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """View document details."""
    model = EmployeeDocument
    template_name = 'hr/documents/detail.html'
    context_object_name = 'document'


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """Create a new document record."""
    model = EmployeeDocument
    template_name = 'hr/documents/form.html'
    fields = [
        'employee', 'document_type', 'document_number',
        'issue_date', 'expiry_date', 'issuing_authority',
        'file_path', 'is_verified',
    ]
    success_url = reverse_lazy('hr:document_list')

    def form_valid(self, form):
        messages.success(self.request, 'Document created successfully.')
        return super().form_valid(form)


# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

class AssetListView(LoginRequiredMixin, ListView):
    """List all HR assets."""
    model = HRAsset
    template_name = 'hr/assets/list.html'
    context_object_name = 'assets'
    paginate_by = 50

    def get_queryset(self):
        queryset = HRAsset.objects.select_related('asset_type').order_by('asset_number')

        # Filter by type
        asset_type = self.request.GET.get('type')
        if asset_type:
            queryset = queryset.filter(asset_type_id=asset_type)

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asset_types'] = AssetType.objects.all()
        return context


class AssetDetailView(LoginRequiredMixin, DetailView):
    """View asset details."""
    model = HRAsset
    template_name = 'hr/assets/detail.html'
    context_object_name = 'asset'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignments'] = self.object.assignments.select_related(
            'employee__person'
        ).order_by('-assigned_date')
        return context


class AssetCreateView(LoginRequiredMixin, CreateView):
    """Create a new asset."""
    model = HRAsset
    template_name = 'hr/assets/form.html'
    fields = [
        'asset_type', 'asset_number', 'description',
        'serial_number', 'plate_number', 'phone_number',
        'status',
    ]
    success_url = reverse_lazy('hr:asset_list')

    def form_valid(self, form):
        messages.success(self.request, 'Asset created successfully.')
        return super().form_valid(form)


class AssetAssignView(LoginRequiredMixin, CreateView):
    """Assign an asset to an employee."""
    model = AssetAssignment
    template_name = 'hr/assets/assign.html'
    fields = ['asset', 'employee', 'assigned_date', 'notes']

    def get_success_url(self):
        return reverse('hr:asset_detail', kwargs={'pk': self.object.asset.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Asset assigned successfully.')
        # Update asset status
        asset = form.instance.asset
        asset.status = 'ASSIGNED'
        asset.save()
        return super().form_valid(form)
