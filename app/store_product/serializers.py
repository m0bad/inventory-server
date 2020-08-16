from rest_framework import serializers

from core.models import StoreProduct


class StoreProductSerializer(serializers.ModelSerializer):
    """Serializer for StoreProduct objects """

    class Meta:
        model = StoreProduct
        fields = ('id',)
        read_only_fields = ('id',)