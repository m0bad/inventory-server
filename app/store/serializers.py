from rest_framework import serializers

from core.models import Store


class StoreSerializer(serializers.ModelSerializer):
    """Serializes Store objects"""

    class Meta:
        model = Store
        fields = ('id', 'name', 'city', 'cash')
        read_only_fields = ('id',)

