"""
Production Department URL Configuration
"""

from django.urls import path
from . import views
from . import analytics_views

app_name = 'production'

urlpatterns = [
    # Dashboard
    path('', views.ProductionDashboardView.as_view(), name='dashboard'),

    # Bit Designs
    path('designs/', views.BitDesignListView.as_view(), name='bitdesign-list'),
    path('designs/hub/', views.BitDesignHubView.as_view(), name='bitdesign-hub'),
    path('designs/<int:pk>/', views.BitDesignDetailView.as_view(), name='bitdesign-detail'),
    path('designs/create/', views.BitDesignCreateView.as_view(), name='bitdesign-create'),
    path('designs/<int:pk>/edit/', views.BitDesignUpdateView.as_view(), name='bitdesign-edit'),
    path('designs/<int:pk>/mat-levels/', views.BitMatLevelListView.as_view(), name='bitdesign-mat-levels'),

    # MAT Level Operations
    path('designs/<int:pk>/create-level2/', views.BitMatCreateLevel2FromDesignView.as_view(), name='design-create-level2'),
    path('mats/<int:pk>/clone-branch/', views.BitMatCloneAsBranchView.as_view(), name='mat-clone-branch'),
    path('mats/<int:pk>/create-next-level/', views.BitMatCreateNextLevelView.as_view(), name='mat-create-next-level'),

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
    path('jobcards/<int:pk>/print/', views.JobCardPrintView.as_view(), name='jobcard-print'),
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

    # Route Management
    path('jobcards/<int:pk>/regenerate-route/', views.regenerate_route_steps_view, name='jobcard-regenerate-route'),
    path('route-steps/<int:pk>/status/<str:new_status>/', views.update_route_step_status_view, name='routestep-update-status'),

    # Evaluations
    path('evaluations/', views.EvaluationSummaryListView.as_view(), name='evaluation-list'),
    path('evaluations/create/', views.EvaluationSummaryCreateView.as_view(), name='evaluation-create'),

    # Non-Conformance Reports (NCR)
    path('ncr/', views.NCRListView.as_view(), name='ncr-list'),
    path('ncr/<int:pk>/', views.NCRDetailView.as_view(), name='ncr-detail'),
    path('ncr/create/', views.NCRCreateView.as_view(), name='ncr-create'),

    # Production Holds
    path('holds/', views.ProductionHoldListView.as_view(), name='hold-list'),
    path('holds/create/', views.ProductionHoldCreateView.as_view(), name='hold-create'),

    # WIP Dashboard & Analytics
    path('wip/', analytics_views.WIPDashboardView.as_view(), name='wip-dashboard'),
    path('analytics/process/', analytics_views.ProcessAnalyticsView.as_view(), name='process-analytics'),
    path('analytics/kpi/', analytics_views.KPIDashboardView.as_view(), name='kpi-dashboard'),

    # Maintenance
    path('maintenance/', analytics_views.MaintenanceRequestListView.as_view(), name='maintenance-list'),
    path('maintenance/create/', analytics_views.MaintenanceRequestCreateView.as_view(), name='maintenance-create'),
    path('equipment/', analytics_views.EquipmentListView.as_view(), name='equipment-list'),

    # Process Correction Requests
    path('corrections/', views.ProcessCorrectionRequestListView.as_view(), name='correction-request-list'),
    path('corrections/<int:pk>/', views.ProcessCorrectionRequestDetailView.as_view(), name='correction-request-detail'),
    path('corrections/create/', views.ProcessCorrectionRequestCreateView.as_view(), name='correction-request-create'),
    path('corrections/<int:pk>/approve/', views.approve_correction_request, name='correction-request-approve'),
    path('corrections/<int:pk>/reject/', views.reject_correction_request, name='correction-request-reject'),
    path('corrections/<int:pk>/execute/', views.execute_correction_request, name='correction-request-execute'),

    # Execution Logs
    path('execution-logs/', views.ProcessExecutionLogListView.as_view(), name='execution-log-list'),

    # Repair Workflow - Repair History
    path('repair-history/', views.RepairHistoryListView.as_view(), name='repair-history-list'),
    path('repair-history/<int:pk>/', views.RepairHistoryDetailView.as_view(), name='repair-history-detail'),

    # Repair Workflow - Repair Decisions
    path('repair-decisions/create/', views.RepairDecisionCreateView.as_view(), name='repair-decision-create'),
    path('repair-decisions/<int:pk>/', views.RepairDecisionDetailView.as_view(), name='repair-decision-detail'),

    # Repair Workflow - BOM Tracking
    path('actual-bom/', views.ActualBOMListView.as_view(), name='actual-bom-list'),
    path('actual-bom/<int:pk>/edit/', views.ActualBOMUpdateView.as_view(), name='actual-bom-edit'),

    # Repair Workflow - Cutter Layout & Installation
    path('designs/<int:pk>/cutter-layout/', views.CutterLayoutView.as_view(), name='cutter-layout'),
    path('workorders/<int:work_order_id>/cutter-installation/', views.CutterInstallationRecordView.as_view(), name='cutter-installation-record'),
    path('cutter-installations/', views.CutterInstallationListView.as_view(), name='cutter-installation-list'),
]
