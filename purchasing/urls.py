from django.urls import path
from . import views
from . import real_life_views

app_name = 'purchasing'

urlpatterns = [
    # Dashboard
    path('', views.PurchasingDashboardView.as_view(), name='dashboard'),

    # Purchase Requests
    path('pr/', views.PurchaseRequestListView.as_view(), name='pr_list'),
    path('pr/<int:pk>/', views.PurchaseRequestDetailView.as_view(), name='pr_detail'),
    path('pr/create/', views.PurchaseRequestCreateView.as_view(), name='pr_create'),
    path('pr/<int:pk>/edit/', views.PurchaseRequestUpdateView.as_view(), name='pr_update'),

    # Purchase Orders
    path('po/', views.PurchaseOrderListView.as_view(), name='po_list'),
    path('po/<int:pk>/', views.PurchaseOrderDetailView.as_view(), name='po_detail'),
    path('po/create/', views.PurchaseOrderCreateView.as_view(), name='po_create'),
    path('po/<int:pk>/edit/', views.PurchaseOrderUpdateView.as_view(), name='po_update'),

    # Goods Receipts
    path('grn/', views.GoodsReceiptListView.as_view(), name='grn_list'),
    path('grn/<int:pk>/', views.GoodsReceiptDetailView.as_view(), name='grn_detail'),
    path('grn/create/', views.GoodsReceiptCreateView.as_view(), name='grn_create'),
    path('grn/<int:pk>/edit/', views.GoodsReceiptUpdateView.as_view(), name='grn_update'),

    # Goods Returns (RTV)
    path('returns/', real_life_views.GoodsReturnListView.as_view(), name='goods_return_list'),
    path('returns/<int:pk>/', real_life_views.GoodsReturnDetailView.as_view(), name='goods_return_detail'),
    path('returns/create/<int:grn_pk>/', real_life_views.GoodsReturnCreateView.as_view(), name='goods_return_create'),
    path('returns/<int:pk>/submit/', real_life_views.GoodsReturnSubmitView.as_view(), name='goods_return_submit'),

    # GRN Corrections
    path('corrections/', real_life_views.GRNCorrectionListView.as_view(), name='grn_correction_list'),
    path('corrections/<int:pk>/', real_life_views.GRNCorrectionDetailView.as_view(), name='grn_correction_detail'),
    path('corrections/create/<int:grn_line_pk>/', real_life_views.GRNCorrectionCreateView.as_view(), name='grn_correction_create'),
    path('corrections/<int:pk>/approve/', real_life_views.GRNCorrectionApproveView.as_view(), name='grn_correction_approve'),

    # Quick Actions for Real-Life Scenarios
    path('quick-actions/', real_life_views.QuickActionsMenuView.as_view(), name='quick_actions'),
]
