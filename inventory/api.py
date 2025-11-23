"""
REST API Views for Inventory and Purchasing
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from .models import Item, StockLevel, StockTransaction, Supplier, Warehouse
from purchasing.models import PurchaseOrder, GoodsReceipt


# Serializers
class ItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    uom_code = serializers.CharField(source='unit_of_measure.code', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'item_code', 'name', 'category', 'category_name',
                  'unit_of_measure', 'uom_code', 'item_type', 'active',
                  'reorder_level', 'description']


class StockLevelSerializer(serializers.ModelSerializer):
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    item_name = serializers.CharField(source='item.name', read_only=True)
    location_code = serializers.CharField(source='location.code', read_only=True)
    warehouse_code = serializers.CharField(source='location.warehouse.code', read_only=True)

    class Meta:
        model = StockLevel
        fields = ['id', 'item', 'item_code', 'item_name', 'location',
                  'location_code', 'warehouse_code', 'condition_type',
                  'ownership_type', 'quantity', 'last_updated']


class StockTransactionSerializer(serializers.ModelSerializer):
    item_code = serializers.CharField(source='item.item_code', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True)

    class Meta:
        model = StockTransaction
        fields = ['id', 'item', 'item_code', 'transaction_type', 'quantity',
                  'from_location', 'to_location', 'condition_type', 'ownership_type',
                  'reference', 'performed_at', 'performed_by', 'performed_by_name', 'notes']


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'code', 'name', 'country', 'contact_person',
                  'phone', 'email', 'active']


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'code', 'name', 'address', 'active']


# ViewSets
class ItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Items.

    list: Get all items
    retrieve: Get single item
    create: Create new item
    update: Update item
    destroy: Delete item

    Custom actions:
    - low_stock: Get items below reorder level
    """
    queryset = Item.objects.filter(active=True).select_related(
        'category', 'unit_of_measure', 'preferred_supplier'
    )
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['category', 'item_type', 'active']
    search_fields = ['item_code', 'name', 'description']
    ordering_fields = ['item_code', 'name', 'created_at']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get items with stock below reorder level."""
        from django.db.models import Sum, F

        items = Item.objects.filter(active=True).annotate(
            total_stock=Sum('stock_levels__quantity')
        ).filter(
            total_stock__lt=F('reorder_level')
        )

        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)


class StockLevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Stock Levels (Read-only).

    list: Get all stock levels
    retrieve: Get single stock level

    Custom actions:
    - by_item: Get stock for specific item
    - by_warehouse: Get stock for specific warehouse
    """
    queryset = StockLevel.objects.filter(quantity__gt=0).select_related(
        'item', 'location__warehouse', 'condition_type', 'ownership_type'
    )
    serializer_class = StockLevelSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['item', 'location', 'condition_type', 'ownership_type']

    @action(detail=False, methods=['get'])
    def by_item(self, request):
        """Get stock levels for a specific item."""
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response({'error': 'item_id parameter required'},
                          status=status.HTTP_400_BAD_REQUEST)

        stock_levels = self.queryset.filter(item_id=item_id)
        serializer = self.get_serializer(stock_levels, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_warehouse(self, request):
        """Get stock levels for a specific warehouse."""
        warehouse_id = request.query_params.get('warehouse_id')
        if not warehouse_id:
            return Response({'error': 'warehouse_id parameter required'},
                          status=status.HTTP_400_BAD_REQUEST)

        stock_levels = self.queryset.filter(location__warehouse_id=warehouse_id)
        serializer = self.get_serializer(stock_levels, many=True)
        return Response(serializer.data)


class StockTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Stock Transactions (Read-only).

    list: Get all transactions
    retrieve: Get single transaction
    """
    queryset = StockTransaction.objects.all().select_related(
        'item', 'from_location', 'to_location', 'performed_by'
    ).order_by('-performed_at')
    serializer_class = StockTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['item', 'transaction_type', 'performed_by']
    ordering_fields = ['performed_at', 'quantity']


class SupplierViewSet(viewsets.ModelViewSet):
    """API endpoint for Suppliers."""
    queryset = Supplier.objects.filter(active=True)
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['code', 'name', 'country']
    ordering_fields = ['code', 'name']


class WarehouseViewSet(viewsets.ModelViewSet):
    """API endpoint for Warehouses."""
    queryset = Warehouse.objects.filter(active=True)
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name']
