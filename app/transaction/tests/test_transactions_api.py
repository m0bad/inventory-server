from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Transaction, TransactionProduct, StoreProduct, Store, Product

TRANSACTION_URL = reverse('transaction:transaction-list')

def sample_user(user_type, email='user@user.com', password='pass123'):
    return get_user_model().objects.create_user(email=email, user_type=user_type, password=password)

def sample_transaction_payload(trx_type, store_id, created_by, party_id, product_id, amount= '1000.00', quantity = 1):
    """return a transaction object"""
    return {
        'trx_type': trx_type,
        'store_id': store_id,
        'created_by': created_by,
        'party_id': party_id,
        'amount': amount,
        'product_id': product_id,
        'quantity': quantity
    }


class TransactionsGeneralApiTest(TestCase):
    """Test the General Transactions APIs"""

    def setUp(self):
        self.admin = sample_user(user_type='Admin', email='admin@admin.com')
        self.supplier = sample_user(user_type='Supplier', email='supplier@supplier.com')
        self.customer = sample_user(user_type='Customer', email='customer@customer.com')
        self.store = Store.objects.create(name='Store#1', city='Cairo')
        self.product = Product.objects.create(supplier_id=self.supplier, name='TestProduct', price='1000.00', image='')
        self.payload = sample_transaction_payload(
            trx_type='OUT',
            store_id=self.store.id,
            created_by=self.supplier.id,
            party_id=self.customer.id,
            product_id=self.product.id,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.customer)

    def test_transaction_amount_and_quantity_not_equal_to_product_price_fails(self):
        payload = sample_transaction_payload(
            trx_type='IN',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.supplier.id,
            product_id=self.product.id,
            amount='11000',
            quantity=9
        )

        res = self.client.post(TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_created_by_other_than_admin_fails(self):
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_wrong_trx_type_fails(self):
        self.payload['trx_type'] = 'IN/OUT'
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_store_fails(self):
        self.payload.pop('store_id')
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_amount_fails(self):
        self.payload.pop('amount')
        res = self.client.post(TRANSACTION_URL, self.payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_party_fails(self):
        self.payload.pop('party_id')
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_created_by_fails(self):
        self.payload.pop('created_by')
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_trx_type_fails(self):
        self.payload.pop('trx_type')
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_product_fails(self):
        self.payload.pop('product_id')
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_no_quantity_type_fails(self):
        self.payload.pop('quantity')
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_with_negative_quantity_fails(self):
        self.payload['quantity'] = -1
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_with_negative_amount_fails(self):
        self.payload['amount'] = -1
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

class TransactionsInApiTest(TestCase):
    """Test the IN Transactions APIs"""

    def setUp(self):
        self.admin = sample_user(user_type='Admin', email='admin@admin.com')
        self.supplier = sample_user(user_type='Supplier', email='supplier@supplier.com')
        self.store = Store.objects.create(name='Store#1', city='Cairo', cash=10000)
        self.product = Product.objects.create(supplier_id=self.supplier, name='TestProduct', price='1000.00', image='')
        self.payload = sample_transaction_payload(
            trx_type='IN',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.supplier.id,
            product_id=self.product.id,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.supplier)


    def test_basic_transaction_in_success(self):
        """Test that a supplier can make a successful IN transaction"""
        res = self.client.post(TRANSACTION_URL, self.payload)
        transaction = Transaction.objects.all()
        transaction_products = TransactionProduct.objects.all()
        store_products = StoreProduct.objects.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(transaction), 1)
        self.assertEqual(len(transaction_products), 1)
        self.assertEqual(len(store_products), 1)
        self.assertEqual(list(transaction_products)[0].product_id, list(store_products)[0].product_id)


    def test_transaction_in_with_two_store_products_success(self):
        """Test that a supplier can make more than one transaction successfully"""
        res1 = self.client.post(TRANSACTION_URL, self.payload)
        res2 = self.client.post(TRANSACTION_URL, self.payload)
        transaction = Transaction.objects.all()
        transaction_products = TransactionProduct.objects.all()
        store_products = StoreProduct.objects.all()
        store_product_record = StoreProduct.objects.get(store_id=self.store.id, product_id=self.product.id)

        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(transaction), 2)
        self.assertEqual(len(transaction_products), 2)
        self.assertEqual(len(store_products), 1)
        self.assertEqual(store_product_record.quantity, self.payload['quantity'] * 2)

    def test_transaction_type_in_from_customer_fails(self):
        customer = sample_user(user_type='Customer', email='customer@customer.com')
        self.payload['party_id'] = customer

        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_transaction_in_with_no_enough_money_in_store_fails(self):
        payload = sample_transaction_payload(
            trx_type='IN',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.supplier.id,
            product_id=self.product.id,
            amount='11000',
            quantity=11
        )

        res = self.client.post(TRANSACTION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class TransactionsOutApiTest(TestCase):
    """Test the OUT Transactions APIs"""

    def setUp(self):
        self.admin = sample_user(user_type='Admin', email='admin@admin.com')
        self.customer = sample_user(user_type='Customer', email='customer@customer.com')
        self.supplier = sample_user(user_type='Supplier', email='supplier@supplier.com')
        self.store = Store.objects.create(name='Store', city='Cairo', cash=10000)
        self.product = Product.objects.create(supplier_id=self.supplier, name='TestProduct', price='1000.00', image='')
        self.payload = sample_transaction_payload(
            trx_type='OUT',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.customer.id,
            product_id=self.product.id,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.supplier)

    def test_transaction_out_with_no_available_products_fails(self):
        """Test that a customer can't make a successful OUT transaction with there is no products in the store"""
        res = self.client.post(TRANSACTION_URL, self.payload)
        transaction = Transaction.objects.all()
        transaction_products = TransactionProduct.objects.all()
        store_product = TransactionProduct.objects.all()

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(transaction), 0)
        self.assertEqual(len(transaction_products), 0)
        self.assertEqual(len(store_product), 0)

    def test_basic_transaction_out_success(self):
        """Test that customer can make an out transaction if there is available products in the store"""
        in_trx_payload = sample_transaction_payload(
            trx_type='IN',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.supplier.id,
            product_id=self.product.id,
            amount='3000.00',
            quantity=3
        )
        out_trx_payload = sample_transaction_payload(
            trx_type='OUT',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.customer.id,
            product_id=self.product.id,
            amount='2000.00',
            quantity=2
        )
        in_res = self.client.post(TRANSACTION_URL, in_trx_payload)
        out_res = self.client.post(TRANSACTION_URL, out_trx_payload)

        transactions_count = Transaction.objects.filter().count()
        transaction_products_count = TransactionProduct.objects.filter().count()
        store_products = StoreProduct.objects.get(product_id=self.product)

        self.assertEqual(in_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(out_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(transactions_count, 2)
        self.assertEqual(transaction_products_count, 2)
        self.assertEqual(store_products.quantity, 1)


    def test_transaction_type_out_from_supplier_fails(self):
        self.payload['party_id'] = self.supplier
        res = self.client.post(TRANSACTION_URL, self.payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_transaction_out_with_no_quantity_available_in_store_fails(self):
        """Test that customer can make an out transaction if there is available products in the store"""
        in_trx_payload = sample_transaction_payload(
            trx_type='IN',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.supplier.id,
            product_id=self.product.id,
            amount='5000.00',
            quantity=5
        )
        out_trx_payload = sample_transaction_payload(
            trx_type='OUT',
            store_id=self.store.id,
            created_by=self.admin.id,
            party_id=self.customer.id,
            product_id=self.product.id,
            amount='7000.00',
            quantity=7
        )
        in_res = self.client.post(TRANSACTION_URL, in_trx_payload)
        out_res = self.client.post(TRANSACTION_URL, out_trx_payload)

        transactions_count = Transaction.objects.filter().count()
        transaction_products_count = TransactionProduct.objects.filter().count()
        store_products = StoreProduct.objects.get(product_id=self.product)

        self.assertEqual(in_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(out_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(transactions_count, 1)
        self.assertEqual(transaction_products_count, 1)
        self.assertEqual(store_products.quantity, 5)
