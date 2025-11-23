"""
HR URLs - Human Resources Module
"""
from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # HR Home / Employee Portal
    path('', views.hr_home, name='home'),

    # Employee Directory
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),

    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),

    # Leave Management (for employees to view their leaves)
    path('leave/', views.my_leave, name='my_leave'),

    # Attendance (for employees to view their attendance)
    path('attendance/', views.my_attendance, name='my_attendance'),

    # Employee Self-Service Portal
    path('portal/', views.employee_portal, name='employee_portal'),
]
