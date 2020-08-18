from rest_framework import serializers

from core.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    """Serializes Transaction objects"""

    class Meta:
        model = Transaction
        fields = ('id', 'trx_type','store_id', 'created_by', 'party_id', 'amount', 'created_at')
        read_only_fields = ('id', 'trx_type','store_id', 'created_by', 'party_id', 'amount', 'created_at')

