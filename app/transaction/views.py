#TODO: must refactor this file.

from django.db import IntegrityError, transaction
from django import forms
from django.core.exceptions import SuspiciousOperation, ValidationError
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Transaction, TransactionProduct, StoreProduct, User, Store, Product

from transaction import serializers


def validate_trx_type(value):
    if value not in ['IN', 'OUT']:
        raise ValidationError('Transaction type Must be IN or OUT.')

def validate_created_by(value):
    user = User.objects.get(pk=value)
    if user.user_type != 'Admin':
        raise ValidationError('created_by id must belong to Admin user.')


class TransactionValidationForm(forms.Form):
    created_by = forms.IntegerField(validators=[validate_created_by])
    party_id = forms.IntegerField()
    store_id = forms.IntegerField()
    product_id = forms.IntegerField()
    quantity = forms.IntegerField(min_value=0)
    amount = forms.DecimalField(min_value=0)
    trx_type = forms.CharField(validators=[validate_trx_type])


class TransactionViewSet(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Transaction.objects.all()
    serializer_class = serializers.TransactionSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        data = TransactionValidationForm(self.request.data)
        if not data.is_valid():
            raise SuspiciousOperation('Invalid Data')
        else:
            pass

        created_by = User.objects.get(pk=self.request.data['created_by'])
        party_id = User.objects.get(pk=self.request.data['party_id'])
        store_id = Store.objects.get(pk=self.request.data['store_id'])
        product_id = Product.objects.get(pk=self.request.data['product_id'])
        trx_type = self.request.data['trx_type']
        amount = self.request.data['amount']
        quantity = self.request.data['quantity']

        try:
            with transaction.atomic():
                trx = Transaction(
                    created_by=created_by,
                    party_id=party_id,
                    store_id=store_id,
                    trx_type=trx_type,
                    amount=amount,
                )
                trx.save()

                trx_product = TransactionProduct(
                    trx_id=trx,
                    product_id=product_id,
                    quantity=quantity,
                )
                trx_product.save()

                store_products_exists = StoreProduct.objects.filter(
                    store_id=store_id,
                    product_id=product_id
                ).exists()
                if store_products_exists:
                    store_product = StoreProduct.objects.get(
                    store_id=store_id,
                    product_id=product_id
                )
                    if trx_type == 'IN':
                        store_product.quantity += quantity
                    else:
                        store_product.quantity -= quantity

                    store_product.save()
                else:
                    store_product = StoreProduct(
                        store_id=store_id,
                        product_id=product_id,
                        quantity=quantity,
                    )
                    store_product.save()

        except IntegrityError:
            print('Something Went Wrong in Transactions View atomic handler.')
