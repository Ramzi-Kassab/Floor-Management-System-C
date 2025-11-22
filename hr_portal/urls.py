"""
HR Portal URL Configuration
Namespace: 'hr_portal'
Base path: /portal/

Employee self-service portal for HR functions.
"""
from django.urls import path
from . import views

app_name = 'hr_portal'

urlpatterns = [
    # Dashboard
    path('', views.PortalDashboardView.as_view(), name='dashboard'),

    # My Profile
    path('profile/', views.MyProfileView.as_view(), name='my_profile'),

    # My Leave Requests
    path('leaves/', views.MyLeaveListView.as_view(), name='my_leaves'),
    path('leaves/new/', views.MyLeaveCreateView.as_view(), name='my_leave_create'),
    path('leaves/<int:pk>/', views.MyLeaveDetailView.as_view(), name='my_leave_detail'),

    # My General Requests (certificates, letters, data updates, etc.)
    path('requests/', views.MyRequestListView.as_view(), name='my_requests'),
    path('requests/new/', views.MyRequestCreateView.as_view(), name='my_request_create'),
    path('requests/<int:pk>/', views.MyRequestDetailView.as_view(), name='my_request_detail'),

    # My Attendance (read-only view)
    path('attendance/', views.MyAttendanceView.as_view(), name='my_attendance'),

    # My Training
    path('training/', views.MyTrainingView.as_view(), name='my_training'),

    # My Documents
    path('documents/', views.MyDocumentsView.as_view(), name='my_documents'),

    # My Assets (assigned to me)
    path('assets/', views.MyAssetsView.as_view(), name='my_assets'),
]
