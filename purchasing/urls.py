from django.urls import path
from . import views

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
]
