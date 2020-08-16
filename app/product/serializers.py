from rest_framework import serializers

from core.models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Serializes Product objects"""

    class Meta:
        model = Product
        fields = ('id', 'name', 'supplier_id', 'price', 'image', 'created_at', 'updated_at')
        read_only_fields = ('id', 'supplier_id')

