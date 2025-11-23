"""
HR Views - Human Resources Module
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import (
    HREmployee, Department, Position,
    LeaveRequest, AttendanceRecord
)


def hr_home(request):
    """HR Module Home Page."""
    context = {
        'total_employees': HREmployee.objects.filter(is_deleted=False).count(),
        'total_departments': Department.objects.filter(is_active=True).count(),
        'active_employees': HREmployee.objects.filter(
            status='ACTIVE',
            is_deleted=False
        ).count(),
    }
    return render(request, 'hr/home.html', context)


def employee_list(request):
    """List all employees."""
    employees = HREmployee.objects.filter(
        is_deleted=False
    ).select_related('person', 'department', 'position').order_by('employee_number')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        employees = employees.filter(
            Q(employee_number__icontains=search_query) |
            Q(person__first_name__icontains=search_query) |
            Q(person__last_name__icontains=search_query)
        )

    context = {
        'employees': employees,
        'search_query': search_query,
    }
    return render(request, 'hr/employee_list.html', context)


def employee_detail(request, pk):
    """Employee detail view."""
    employee = get_object_or_404(
        HREmployee.objects.select_related('person', 'department', 'position'),
        pk=pk,
        is_deleted=False
    )
    context = {
        'employee': employee,
    }
    return render(request, 'hr/employee_detail.html', context)


def department_list(request):
    """List all departments."""
    departments = Department.objects.filter(
        is_active=True
    ).annotate(
        employee_count=Count('employees')
    ).order_by('code')

    context = {
        'departments': departments,
    }
    return render(request, 'hr/department_list.html', context)


def department_detail(request, pk):
    """Department detail view."""
    department = get_object_or_404(Department, pk=pk, is_active=True)
    employees = department.employees.filter(is_deleted=False).select_related('person', 'position')

    context = {
        'department': department,
        'employees': employees,
    }
    return render(request, 'hr/department_detail.html', context)


@login_required
def my_leave(request):
    """Employee's own leave requests."""
    try:
        employee = request.user.hr_employee
        leave_requests = LeaveRequest.objects.filter(
            employee=employee
        ).select_related('leave_type').order_by('-start_date')

        context = {
            'employee': employee,
            'leave_requests': leave_requests,
        }
        return render(request, 'hr/my_leave.html', context)
    except HREmployee.DoesNotExist:
        context = {
            'error': 'No employee record found for your account.'
        }
        return render(request, 'hr/my_leave.html', context)


@login_required
def my_attendance(request):
    """Employee's own attendance records."""
    try:
        employee = request.user.hr_employee
        attendance_records = AttendanceRecord.objects.filter(
            employee=employee
        ).order_by('-date')[:30]  # Last 30 days

        context = {
            'employee': employee,
            'attendance_records': attendance_records,
        }
        return render(request, 'hr/my_attendance.html', context)
    except HREmployee.DoesNotExist:
        context = {
            'error': 'No employee record found for your account.'
        }
        return render(request, 'hr/my_attendance.html', context)


@login_required
def employee_portal(request):
    """Employee Self-Service Portal."""
    try:
        employee = request.user.hr_employee

        # Get recent leave requests
        recent_leaves = LeaveRequest.objects.filter(
            employee=employee
        ).select_related('leave_type').order_by('-start_date')[:5]

        # Get recent attendance
        recent_attendance = AttendanceRecord.objects.filter(
            employee=employee
        ).order_by('-date')[:7]

        context = {
            'employee': employee,
            'recent_leaves': recent_leaves,
            'recent_attendance': recent_attendance,
        }
        return render(request, 'hr/employee_portal.html', context)
    except HREmployee.DoesNotExist:
        context = {
            'error': 'No employee record found for your account.'
        }
        return render(request, 'hr/employee_portal.html', context)
