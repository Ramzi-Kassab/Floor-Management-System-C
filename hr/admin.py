"""
HR Admin Configuration - Version C
Django admin interface for HR models.
"""
from django.contrib import admin
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


# Core Models
@admin.register(HRPerson)
class HRPersonAdmin(admin.ModelAdmin):
    list_display = ['national_id', 'full_name_en', 'gender', 'nationality_iso2', 'date_of_birth']
    list_filter = ['gender', 'nationality_iso2', 'marital_status']
    search_fields = ['first_name_en', 'last_name_en', 'national_id', 'iqama_number']
    ordering = ['last_name_en', 'first_name_en']
    date_hierarchy = 'created_at'


@admin.register(HREmployee)
class HREmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_no', 'person', 'department', 'position', 'status', 'hire_date']
    list_filter = ['status', 'department']
    search_fields = ['employee_no', 'person__first_name_en', 'person__last_name_en']
    raw_id_fields = ['person', 'user']
    ordering = ['employee_no']
    date_hierarchy = 'hire_date'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'parent', 'cost_center', 'is_active']
    list_filter = ['is_active']
    search_fields = ['code', 'name']
    ordering = ['code']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'grade_level', 'is_supervisory', 'is_active']
    list_filter = ['category', 'is_supervisory', 'is_active']
    search_fields = ['code', 'title']
    ordering = ['code']


# Employment Models
@admin.register(HRContract)
class HRContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'employee', 'contract_type', 'start_date', 'end_date', 'is_active']
    list_filter = ['contract_type', 'is_active']
    search_fields = ['contract_number', 'employee__employee_no']
    raw_id_fields = ['employee']
    date_hierarchy = 'start_date'


@admin.register(HRShiftTemplate)
class HRShiftTemplateAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'start_time', 'end_time', 'is_night_shift', 'is_active']
    list_filter = ['is_night_shift', 'is_active']
    search_fields = ['code', 'name']


# Leave Models
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'is_paid', 'requires_approval', 'max_days_per_year', 'is_active']
    list_filter = ['is_paid', 'requires_approval', 'is_active']
    search_fields = ['code', 'name']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'days_count', 'status', 'approved_by']
    list_filter = ['status', 'leave_type']
    search_fields = ['employee__employee_no', 'employee__person__first_name_en', 'employee__person__last_name_en']
    raw_id_fields = ['employee', 'approved_by']
    date_hierarchy = 'start_date'


# Attendance
@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in', 'check_out', 'late_minutes', 'source']
    list_filter = ['status', 'source']
    search_fields = ['employee__employee_no']
    raw_id_fields = ['employee']
    date_hierarchy = 'date'


# Training Models
@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'category', 'duration_hours', 'is_mandatory', 'is_active']
    list_filter = ['category', 'is_mandatory', 'is_active']
    search_fields = ['code', 'title']


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['program', 'session_date', 'start_time', 'location', 'trainer', 'status']
    list_filter = ['status', 'program']
    search_fields = ['program__title', 'trainer']
    date_hierarchy = 'session_date'


@admin.register(EmployeeTraining)
class EmployeeTrainingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'session', 'attended', 'passed', 'certificate_issued']
    list_filter = ['attended', 'passed', 'certificate_issued']
    search_fields = ['employee__employee_no']
    raw_id_fields = ['employee', 'session']


# Document Models
@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'requires_renewal', 'renewal_notice_days']
    list_filter = ['requires_renewal']
    search_fields = ['code', 'name']


@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'document_type', 'document_number', 'issue_date', 'expiry_date', 'is_verified']
    list_filter = ['document_type', 'is_verified']
    search_fields = ['employee__employee_no', 'document_number']
    raw_id_fields = ['employee']
    date_hierarchy = 'created_at'


# Qualification Models
@admin.register(QualificationLevel)
class QualificationLevelAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'level_order']
    search_fields = ['code', 'name']


@admin.register(EmployeeQualification)
class EmployeeQualificationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'qualification_level', 'field_of_study', 'institution', 'completion_date']
    list_filter = ['qualification_level', 'is_verified']
    search_fields = ['employee__employee_no', 'field_of_study', 'institution']
    raw_id_fields = ['employee']


# Administration/Asset Models
@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'requires_serial_number']
    search_fields = ['code', 'name']


@admin.register(HRAsset)
class HRAssetAdmin(admin.ModelAdmin):
    list_display = ['asset_number', 'asset_type', 'description', 'status']
    list_filter = ['asset_type', 'status']
    search_fields = ['asset_number', 'description', 'serial_number', 'plate_number', 'phone_number']


@admin.register(AssetAssignment)
class AssetAssignmentAdmin(admin.ModelAdmin):
    list_display = ['asset', 'employee', 'assigned_date', 'returned_date']
    list_filter = ['assigned_date']
    search_fields = ['asset__asset_number', 'employee__employee_no']
    raw_id_fields = ['asset', 'employee']
    date_hierarchy = 'assigned_date'


# Contact Models
@admin.register(HRPhone)
class HRPhoneAdmin(admin.ModelAdmin):
    list_display = ['person', 'phone_number', 'phone_type', 'is_primary', 'is_whatsapp']
    list_filter = ['phone_type', 'is_primary', 'is_whatsapp']
    search_fields = ['phone_number', 'person__first_name_en', 'person__last_name_en']
    raw_id_fields = ['person']


@admin.register(HREmail)
class HREmailAdmin(admin.ModelAdmin):
    list_display = ['person', 'email', 'email_type', 'is_primary']
    list_filter = ['email_type', 'is_primary']
    search_fields = ['email', 'person__first_name_en', 'person__last_name_en']
    raw_id_fields = ['person']
