"""
HR Admin Interface - Floor Management System
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Department, Position, HRPeople, HREmployee, HRPhone, HREmail,
    LeaveType, LeavePolicy, LeaveBalance, LeaveRequest,
    AttendanceRecord, OvertimeRequest,
    DocumentType, EmployeeDocument,
    QualificationLevel, EmployeeQualification
)


# Inline admins
class HRPhoneInline(admin.TabularInline):
    model = HRPhone
    extra = 1
    fields = ['phone_type', 'phone_number', 'is_primary']


class HREmailInline(admin.TabularInline):
    model = HREmail
    extra = 1
    fields = ['email_type', 'email_address', 'is_primary']


class EmployeeDocumentInline(admin.TabularInline):
    model = EmployeeDocument
    extra = 0
    fields = ['document_type', 'document_number', 'expiry_date', 'status']
    readonly_fields = ['status']


class EmployeeQualificationInline(admin.TabularInline):
    model = EmployeeQualification
    extra = 0
    fields = ['title', 'institution', 'completion_date', 'is_verified']


# Department Admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent_department', 'department_head', 'employee_count_display', 'is_active']
    list_filter = ['is_active', 'parent_department']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': ['code', 'name', 'description']
        }),
        ('Organization', {
            'fields': ['parent_department', 'department_head', 'cost_center']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]

    def employee_count_display(self, obj):
        count = obj.get_employee_count()
        return format_html('<strong>{}</strong> employees', count)
    employee_count_display.short_description = 'Employees'


# Position Admin
@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'department', 'level', 'headcount_display', 'is_active']
    list_filter = ['is_active', 'department', 'level']
    search_fields = ['code', 'title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Basic Information', {
            'fields': ['code', 'title', 'description']
        }),
        ('Organization', {
            'fields': ['department', 'reports_to', 'level']
        }),
        ('Headcount', {
            'fields': ['min_headcount', 'max_headcount']
        }),
        ('Requirements', {
            'fields': ['required_qualifications', 'required_skills'],
            'classes': ['collapse']
        }),
        ('Status', {
            'fields': ['is_active']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]

    def headcount_display(self, obj):
        current = obj.get_current_headcount()
        max_count = obj.max_headcount
        color = 'green' if current <= max_count else 'red'
        return format_html(
            '<span style="color: {};">{} / {}</span>',
            color, current, max_count
        )
    headcount_display.short_description = 'Headcount (Current/Max)'


# HRPeople Admin
@admin.register(HRPeople)
class HRPeopleAdmin(admin.ModelAdmin):
    list_display = ['national_id', 'get_full_name', 'gender', 'date_of_birth', 'primary_phone']
    list_filter = ['gender', 'marital_status', 'country']
    search_fields = ['first_name', 'last_name', 'national_id', 'passport_number', 'primary_phone']
    readonly_fields = ['created_at', 'updated_at', 'get_age']
    fieldsets = [
        ('Personal Information', {
            'fields': ['first_name', 'middle_name', 'last_name', 'full_name_arabic']
        }),
        ('Demographics', {
            'fields': ['date_of_birth', 'get_age', 'gender', 'marital_status', 'blood_group']
        }),
        ('Identification', {
            'fields': ['national_id', 'passport_number', 'passport_expiry']
        }),
        ('Contact Information', {
            'fields': ['primary_phone', 'primary_email']
        }),
        ('Address', {
            'fields': ['address_line1', 'address_line2', 'city', 'state_province', 'postal_code', 'country'],
            'classes': ['collapse']
        }),
        ('Emergency Contact', {
            'fields': ['emergency_contact_name', 'emergency_contact_relationship', 'emergency_contact_phone'],
            'classes': ['collapse']
        }),
        ('Additional', {
            'fields': ['photo', 'notes'],
            'classes': ['collapse']
        }),
        ('Metadata', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def get_age(self, obj):
        age = obj.get_age()
        return f"{age} years" if age else "N/A"
    get_age.short_description = 'Age'


# HREmployee Admin
@admin.register(HREmployee)
class HREmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_number', 'get_full_name', 'department', 'position', 'status', 'join_date']
    list_filter = ['status', 'employment_type', 'department', 'is_deleted']
    search_fields = ['employee_number', 'person__first_name', 'person__last_name', 'person__national_id']
    readonly_fields = ['created_at', 'updated_at', 'get_service_years', 'get_total_salary']
    inlines = [HRPhoneInline, HREmailInline, EmployeeDocumentInline, EmployeeQualificationInline]
    date_hierarchy = 'join_date'

    fieldsets = [
        ('Employee Identification', {
            'fields': ['person', 'employee_number', 'badge_number', 'user']
        }),
        ('Organization', {
            'fields': ['department', 'position', 'reports_to']
        }),
        ('Employment Details', {
            'fields': ['status', 'employment_type']
        }),
        ('Important Dates', {
            'fields': ['join_date', 'probation_end_date', 'confirmation_date', 'termination_date', 'get_service_years']
        }),
        ('Compensation', {
            'fields': ['basic_salary', 'housing_allowance', 'transport_allowance', 'other_allowance', 'get_total_salary']
        }),
        ('Work Schedule', {
            'fields': ['work_hours_per_day', 'work_days_per_week']
        }),
        ('Leave Entitlements', {
            'fields': ['annual_leave_days', 'sick_leave_days']
        }),
        ('Additional Information', {
            'fields': ['notes'],
            'classes': ['collapse']
        }),
        ('System Fields', {
            'fields': ['is_deleted', 'created_at', 'updated_at', 'created_by'],
            'classes': ['collapse']
        }),
    ]

    def get_service_years(self, obj):
        years = obj.get_service_years()
        return f"{years:.1f} years"
    get_service_years.short_description = 'Service Years'

    def get_total_salary(self, obj):
        total = obj.get_total_salary()
        return f"KD {total:.3f}"
    get_total_salary.short_description = 'Total Salary'


# Leave Management
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_paid', 'requires_approval', 'is_active']
    list_filter = ['is_paid', 'requires_approval', 'is_active']
    search_fields = ['code', 'name']


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'leave_type', 'days_per_year', 'accrual_method', 'allow_carryforward']
    list_filter = ['leave_type', 'accrual_method', 'allow_carryforward']


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'entitled_days', 'used_days', 'available_days_display']
    list_filter = ['year', 'leave_type']
    search_fields = ['employee__employee_number', 'employee__person__first_name', 'employee__person__last_name']

    def available_days_display(self, obj):
        available = obj.get_available_days()
        color = 'green' if available > 0 else 'red'
        return format_html('<span style="color: {};">{:.1f}</span>', color, available)
    available_days_display.short_description = 'Available Days'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'number_of_days', 'status', 'approved_by']
    list_filter = ['status', 'leave_type', 'start_date']
    search_fields = ['employee__employee_number', 'employee__person__first_name', 'employee__person__last_name']
    date_hierarchy = 'start_date'
    readonly_fields = ['submitted_date', 'approved_date']


# Attendance
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'clock_in', 'clock_out', 'regular_hours', 'overtime_hours']
    list_filter = ['status', 'date', 'is_late', 'is_early_departure']
    search_fields = ['employee__employee_number', 'employee__person__first_name', 'employee__person__last_name']
    date_hierarchy = 'date'


@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'hours', 'status', 'approved_by', 'approved_date']
    list_filter = ['status', 'date']
    search_fields = ['employee__employee_number', 'employee__person__first_name', 'employee__person__last_name']
    date_hierarchy = 'date'


# Documents
@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_mandatory', 'has_expiry', 'is_active']
    list_filter = ['is_mandatory', 'has_expiry', 'is_active']


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'document_number', 'issue_date', 'expiry_date', 'status', 'needs_renewal_display']
    list_filter = ['status', 'document_type', 'expiry_date']
    search_fields = ['employee__employee_number', 'document_number']
    readonly_fields = ['verified_date']

    def needs_renewal_display(self, obj):
        if obj.needs_renewal():
            days = obj.days_until_expiry()
            return format_html('<span style="color: red;">Yes ({} days)</span>', days)
        return format_html('<span style="color: green;">No</span>')
    needs_renewal_display.short_description = 'Needs Renewal'


# Qualifications
@admin.register(QualificationLevel)
class QualificationLevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level', 'is_active']
    list_filter = ['is_active']
    ordering = ['-level']


@admin.register(EmployeeQualification)
class EmployeeQualificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'title', 'institution', 'qualification_type', 'completion_date', 'is_verified']
    list_filter = ['qualification_type', 'is_verified', 'qualification_level']
    search_fields = ['employee__employee_number', 'title', 'institution']
    date_hierarchy = 'completion_date'
    readonly_fields = ['verified_date']
