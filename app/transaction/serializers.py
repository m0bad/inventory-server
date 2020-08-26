from rest_framework import serializers

from core.models import Transaction, Store
from store.serializers import StoreSerializer
from user.serializers import UserSerializer

class TransactionSerializer(serializers.ModelSerializer):
    """Serializes Transaction objects"""

    store = StoreSerializer(
        many=False,
        read_only=True
    )
    party = UserSerializer(
        many=False,
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = ('id', 'trx_type','store', 'created_by', 'party', 'amount', 'created_at')
        read_only_fields = ('id', 'trx_type','store', 'created_by', 'party', 'amount', 'created_at')
