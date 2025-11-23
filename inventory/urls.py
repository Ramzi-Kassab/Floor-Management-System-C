from django.urls import path
from . import views
from . import quality_views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.EnhancedDashboardView.as_view(), name='dashboard'),
    path('dashboard/basic/', views.InventoryDashboardView.as_view(), name='dashboard_basic'),

    # Suppliers
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/<int:pk>/', views.SupplierDetailView.as_view(), name='supplier_detail'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.SupplierUpdateView.as_view(), name='supplier_update'),

    # Item Categories
    path('categories/', views.ItemCategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.ItemCategoryCreateView.as_view(), name='category_create'),

    # Items
    path('items/', views.ItemListView.as_view(), name='item_list'),
    path('items/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('items/create/', views.ItemCreateView.as_view(), name='item_create'),
    path('items/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_update'),
    path('items/<int:pk>/qrcode/', views.ItemQRCodeView.as_view(), name='item_qrcode'),

    # Warehouses
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouses/<int:pk>/', views.WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('warehouses/create/', views.WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouses/<int:pk>/edit/', views.WarehouseUpdateView.as_view(), name='warehouse_update'),

    # Locations
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    path('locations/create/', views.LocationCreateView.as_view(), name='location_create'),
    path('locations/<int:pk>/edit/', views.LocationUpdateView.as_view(), name='location_update'),
    path('locations/<int:pk>/qrcode/', views.LocationQRCodeView.as_view(), name='location_qrcode'),

    # Stock
    path('stock/', views.StockLevelListView.as_view(), name='stock_list'),
    path('stock/adjustment/', views.StockAdjustmentView.as_view(), name='stock_adjustment'),
    path('stock/transfer/', views.StockTransferView.as_view(), name='stock_transfer'),
    path('stock/low-stock/', views.LowStockItemsView.as_view(), name='low_stock'),
    path('transactions/', views.StockTransactionListView.as_view(), name='transaction_list'),

    # Export
    path('export/stock/', views.ExportStockView.as_view(), name='export_stock'),
    path('export/transactions/', views.ExportTransactionsView.as_view(), name='export_transactions'),
    path('export/items/', views.ExportItemsView.as_view(), name='export_items'),
    path('export/low-stock/', views.ExportLowStockView.as_view(), name='export_low_stock'),

    # Bulk Operations
    path('bulk/import-items/', views.BulkItemImportView.as_view(), name='bulk_item_import'),
    path('bulk/stock-adjustment/', views.BulkStockAdjustmentView.as_view(), name='bulk_stock_adjustment'),
    path('bulk/batch-update/', views.BatchItemUpdateView.as_view(), name='batch_item_update'),

    # User Preferences
    path('preferences/', views.UserPreferencesView.as_view(), name='user_preferences'),

    # Quality Control & Lifecycle Management
    path('quality/', quality_views.QualityQuickActionsView.as_view(), name='quality_quick_actions'),
    path('quality/dashboard/', quality_views.QualityInspectionDashboardView.as_view(), name='quality_dashboard'),
    path('quality/inspections/', quality_views.QualityInspectionListView.as_view(), name='quality_inspection_list'),

    # Expiry Management
    path('quality/expiry/', quality_views.ExpiryManagementDashboardView.as_view(), name='expiry_dashboard'),
    path('quality/expiry/action/<int:batch_pk>/', quality_views.ExpiredItemActionCreateView.as_view(), name='expired_item_action_create'),

    # Defective Items
    path('quality/defective/', quality_views.DefectiveItemsListView.as_view(), name='defective_items_list'),
    path('quality/defect-report/', quality_views.DefectReportView.as_view(), name='defect_report'),

    # Used Items
    path('quality/used-items/', quality_views.UsedItemsListView.as_view(), name='used_items_list'),
    path('quality/maintenance-schedule/', quality_views.MaintenanceScheduleView.as_view(), name='maintenance_schedule'),
]
