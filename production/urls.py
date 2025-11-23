"""
Production Department URL Configuration
"""

from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    # Dashboard
    path('', views.ProductionDashboardView.as_view(), name='dashboard'),

    # Bit Designs
    path('designs/', views.BitDesignListView.as_view(), name='bitdesign-list'),
    path('designs/<int:pk>/', views.BitDesignDetailView.as_view(), name='bitdesign-detail'),
    path('designs/create/', views.BitDesignCreateView.as_view(), name='bitdesign-create'),
    path('designs/<int:pk>/edit/', views.BitDesignUpdateView.as_view(), name='bitdesign-edit'),

    # Bit Instances
    path('instances/', views.BitInstanceListView.as_view(), name='bitinstance-list'),
    path('instances/<int:pk>/', views.BitInstanceDetailView.as_view(), name='bitinstance-detail'),

    # Work Orders
    path('workorders/', views.WorkOrderListView.as_view(), name='workorder-list'),
    path('workorders/<int:pk>/', views.WorkOrderDetailView.as_view(), name='workorder-detail'),
    path('workorders/create/', views.WorkOrderCreateView.as_view(), name='workorder-create'),
    path('workorders/<int:pk>/edit/', views.WorkOrderUpdateView.as_view(), name='workorder-edit'),

    # Job Cards
    path('jobcards/', views.JobCardListView.as_view(), name='jobcard-list'),
    path('jobcards/<int:pk>/', views.JobCardDetailView.as_view(), name='jobcard-detail'),
    path('jobcards/create/', views.JobCardCreateView.as_view(), name='jobcard-create'),
    path('jobcards/<int:pk>/edit/', views.JobCardUpdateView.as_view(), name='jobcard-edit'),

    # Route Templates
    path('routes/', views.RouteTemplateListView.as_view(), name='routetemplate-list'),
    path('routes/<int:pk>/', views.RouteTemplateDetailView.as_view(), name='routetemplate-detail'),

    # Infiltration Batches
    path('infiltration/', views.InfiltrationBatchListView.as_view(), name='infiltrationbatch-list'),
    path('infiltration/<int:pk>/', views.InfiltrationBatchDetailView.as_view(), name='infiltrationbatch-detail'),
    path('infiltration/create/', views.InfiltrationBatchCreateView.as_view(), name='infiltrationbatch-create'),

    # QR Code functionality
    path('jobcards/<int:pk>/qr/', views.generate_qr_code_view, name='jobcard-qr'),
    path('qr/<str:code>/', views.qr_scan_view, name='qr-scan'),
]
