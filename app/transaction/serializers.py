from rest_framework import serializers

from core.models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    """Serializes Transaction objects"""
    store_id = serializers.RelatedField(source='store', read_only=True)
    created_by = serializers.RelatedField(source='user', read_only=True)
    party_id = serializers.RelatedField(source='user', read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'trx_type','store_id', 'created_by', 'party_id', 'amount', 'created_at')
        read_only_fields = ('id', 'trx_type','store_id', 'created_by', 'party_id', 'amount', 'created_at')

