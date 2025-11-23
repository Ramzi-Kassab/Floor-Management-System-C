from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api

router = DefaultRouter()
router.register(r'items', api.ItemViewSet)
router.register(r'stock-levels', api.StockLevelViewSet)
router.register(r'transactions', api.StockTransactionViewSet)
router.register(r'suppliers', api.SupplierViewSet)
router.register(r'warehouses', api.WarehouseViewSet)

app_name = 'inventory-api'

urlpatterns = [
    path('', include(router.urls)),
]
