"""
HR Back-Office URL Configuration
Namespace: 'hr'
Base path: /hr/

All HR administration and back-office functionality.
"""
from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # Dashboard
    path('', views.HRDashboardView.as_view(), name='dashboard'),

    # Employees
    path('employees/', views.EmployeeListView.as_view(), name='employee_list'),
    path('employees/create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('employees/<int:pk>/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('employees/<int:pk>/edit/', views.EmployeeUpdateView.as_view(), name='employee_update'),

    # People (identity records)
    path('people/', views.PersonListView.as_view(), name='person_list'),
    path('people/create/', views.PersonCreateView.as_view(), name='person_create'),
    path('people/<int:pk>/', views.PersonDetailView.as_view(), name='person_detail'),
    path('people/<int:pk>/edit/', views.PersonUpdateView.as_view(), name='person_update'),

    # Departments
    path('departments/', views.DepartmentListView.as_view(), name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('departments/<int:pk>/', views.DepartmentDetailView.as_view(), name='department_detail'),
    path('departments/<int:pk>/edit/', views.DepartmentUpdateView.as_view(), name='department_update'),

    # Positions
    path('positions/', views.PositionListView.as_view(), name='position_list'),
    path('positions/create/', views.PositionCreateView.as_view(), name='position_create'),
    path('positions/<int:pk>/', views.PositionDetailView.as_view(), name='position_detail'),
    path('positions/<int:pk>/edit/', views.PositionUpdateView.as_view(), name='position_update'),

    # Contracts
    path('contracts/', views.ContractListView.as_view(), name='contract_list'),
    path('contracts/create/', views.ContractCreateView.as_view(), name='contract_create'),
    path('contracts/<int:pk>/', views.ContractDetailView.as_view(), name='contract_detail'),
    path('contracts/<int:pk>/edit/', views.ContractUpdateView.as_view(), name='contract_update'),

    # Leave Management
    path('leaves/', views.LeaveRequestListView.as_view(), name='leave_list'),
    path('leaves/<int:pk>/', views.LeaveRequestDetailView.as_view(), name='leave_detail'),
    path('leaves/<int:pk>/approve/', views.LeaveApproveView.as_view(), name='leave_approve'),
    path('leaves/<int:pk>/reject/', views.LeaveRejectView.as_view(), name='leave_reject'),
    path('leave-types/', views.LeaveTypeListView.as_view(), name='leavetype_list'),
    path('leave-types/create/', views.LeaveTypeCreateView.as_view(), name='leavetype_create'),
    path('leave-types/<int:pk>/edit/', views.LeaveTypeUpdateView.as_view(), name='leavetype_update'),

    # Attendance
    path('attendance/', views.AttendanceListView.as_view(), name='attendance_list'),
    path('attendance/create/', views.AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/<int:pk>/', views.AttendanceDetailView.as_view(), name='attendance_detail'),
    path('attendance/<int:pk>/edit/', views.AttendanceUpdateView.as_view(), name='attendance_update'),
    path('attendance/import/', views.AttendanceImportView.as_view(), name='attendance_import'),

    # Training
    path('training/programs/', views.TrainingProgramListView.as_view(), name='training_program_list'),
    path('training/programs/create/', views.TrainingProgramCreateView.as_view(), name='training_program_create'),
    path('training/programs/<int:pk>/', views.TrainingProgramDetailView.as_view(), name='training_program_detail'),
    path('training/sessions/', views.TrainingSessionListView.as_view(), name='training_session_list'),
    path('training/sessions/create/', views.TrainingSessionCreateView.as_view(), name='training_session_create'),
    path('training/sessions/<int:pk>/', views.TrainingSessionDetailView.as_view(), name='training_session_detail'),

    # Qualifications
    path('qualifications/', views.QualificationListView.as_view(), name='qualification_list'),

    # Documents
    path('documents/', views.DocumentListView.as_view(), name='document_list'),
    path('documents/create/', views.DocumentCreateView.as_view(), name='document_create'),
    path('documents/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),

    # Assets
    path('assets/', views.AssetListView.as_view(), name='asset_list'),
    path('assets/create/', views.AssetCreateView.as_view(), name='asset_create'),
    path('assets/<int:pk>/', views.AssetDetailView.as_view(), name='asset_detail'),
    path('assets/<int:pk>/assign/', views.AssetAssignView.as_view(), name='asset_assign'),
]
