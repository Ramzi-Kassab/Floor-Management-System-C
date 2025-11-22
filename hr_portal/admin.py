"""
HR Portal Admin Configuration - Version C
Django admin interface for HR Portal models.
"""
from django.contrib import admin
from .models import EmployeeRequest


@admin.register(EmployeeRequest)
class EmployeeRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'request_type', 'title', 'status', 'created_at', 'handled_by']
    list_filter = ['status', 'request_type', 'created_at']
    search_fields = ['employee__employee_no', 'title', 'description']
    raw_id_fields = ['employee', 'handled_by']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Request Information', {
            'fields': ('employee', 'request_type', 'title', 'description')
        }),
        ('Status', {
            'fields': ('status', 'handled_by', 'handled_at', 'response_notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
