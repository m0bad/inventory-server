from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Store
from store.serializers import StoreSerializer


STORES_URL = reverse('store:store-list')

def detail_url(store_id):
    """Return Store Detail URL"""
    return reverse('store:store-detail', args=[store_id])


class PublicStoreApiTest(TestCase):
    """Test the public available API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(STORES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_admin_required(self):
        user = get_user_model().objects.create_user(
            'test@test.com',
            'Customer',
            'test123'
        )
        self.client.force_authenticate(user)
        res = self.client.get(STORES_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateStoreApiTest(TestCase):
    """Test the authorized store API"""

    def setUp(self):
        self.admin = get_user_model().objects.create_superuser(
            'admin@admin.com',
            'admin123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.admin)

    def test_list_stores(self):
        """Test that admin can list all available stores"""
        Store.objects.create(name='Store#1', city='Cairo')
        Store.objects.create(name='Store#2', city='Alex')
        Store.objects.create(name='Store#3', city='Assiut')

        res = self.client.get(STORES_URL)

        stores = Store.objects.all().order_by('-name')
        serializer = StoreSerializer(stores, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


    def test_view_store_detail(self):
        """Test viewing a store detail"""
        store = Store.objects.create(name='Store#1', city='Cairo')

        url = detail_url(store.id)
        res = self.client.get(url)

        serializer = StoreSerializer(store)
        self.assertEqual(res.data, serializer.data)


    def test_create_store_without_cash_success(self):
        """Test creating a new store successfully"""
        payload = {
            'name': 'Store#1',
            'city': 'Cairo'
        }

        res = self.client.post(STORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['name'], payload['name'])
        self.assertEqual(res.data['city'], payload['city'])
        self.assertEqual(res.data['cash'], '0.00')

    def test_create_store_with_cash_success(self):
        """Test creating a new store with cash successfully"""
        payload = {
            'name': 'Store#1',
            'city': 'Cairo',
            'cash': '1000.00'
        }

        res = self.client.post(STORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['cash'], payload['cash'])

    def test_create_store_with_same_name_fails(self):
        """Test creating a new store with cash successfully"""
        payload = {
            'name': 'Store#1',
            'city': 'Cairo',
            'cash': '1000.00'
        }
        Store.objects.create(**payload)

        res = self.client.post(STORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_store_name_required(self):
        """Test Store name is required"""
        payload = {
            'name': '',
            'city': 'Cairo',
            'cash': '1000.00'
        }

        res = self.client.post(STORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_store_city_required(self):
        """Test Store city is required"""
        payload = {
            'name': 'test store',
            'city': '',
            'cash': '1000.00'
        }

        res = self.client.post(STORES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_store_success(self):
        """Test update Store is successful"""
        payload = {
            'name': 'test store',
            'city': 'Cairo',
            'cash': '1000.00'
        }

        store = Store.objects.create(**payload)
        url = detail_url(store.id)
        payload['city'] = 'Alex'
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['city'], 'Alex')

    def test_delete_store_success(self):
        """Test delete Store is successful"""
        payload = {
            'name': 'test store',
            'city': 'Cairo',
            'cash': '1000.00'
        }

        store = Store.objects.create(**payload)
        url = detail_url(store.id)
        res = self.client.delete(url)

        stores = Store.objects.all()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(stores), 0)

