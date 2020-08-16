from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Product
from product.serializers import ProductSerializer

PRODUCTS_URL = reverse('product:product-list')
PRODUCT_PAYLOAD = {
    'name': 'LAPTOP-DELL',
    'price': '100.00',
    'image': ''
}


def detail_url(product_id):
    """Return Product Detail URL"""
    return reverse('product:product-detail', args=[product_id])


def sample_product(supplier_id, name='test_product', price='100.00', image=''):
    return Product.objects.create(supplier_id=supplier_id, name=name, price=price, image=image)


class PublicProductApiTest(TestCase):
    """Test the public available API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@user.com',
            'Supplier',
            'user123'
        )

    def test_list_products(self):
        """Test that anyone can list available products"""
        sample_product(supplier_id=self.user)
        sample_product(supplier_id=self.user)
        sample_product(supplier_id=self.user)

        res = self.client.get(PRODUCTS_URL)

        products = Product.objects.all().order_by('-name')
        serializer = ProductSerializer(products, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(len(res.data), 3)

    def test_view_product_detail(self):
        """Test that anyone can view a specific detail"""
        product = sample_product(supplier_id=self.user)

        url = detail_url(product.id)
        res = self.client.get(url)

        serializer = ProductSerializer(product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)


class PrivateProductApiTest(TestCase):
    """Test the authorized product API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@user.com',
            'Supplier',
            'user123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_create_product_as_customer_fails(self):
        """Test creating a new product with Customer user Fails"""
        customer = get_user_model().objects.create_user(
            'customer@customer.com',
            'Customer',
            'user123'
        )
        self.client.force_authenticate(customer)
        res = self.client.post(PRODUCTS_URL, PRODUCT_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_product_success(self):
        """Test creating a new product with Supplier user successfully"""
        res = self.client.post(PRODUCTS_URL, PRODUCT_PAYLOAD)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['supplier_id'], self.user.id)
        self.assertEqual(res.data['name'], PRODUCT_PAYLOAD['name'])
        self.assertEqual(res.data['price'], PRODUCT_PAYLOAD['price'])

    def test_product_name_is_required(self):
        """Test Product name is required"""
        product = {
            'name': '',
            'price': '100.00',
            'image': ''
        }
        res = self.client.post(PRODUCTS_URL, product)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


    def test_product_price_is_required(self):
        """Test Product Supplier ID is required"""
        product = {
            'name': 'LAPTOP',
            'price': '',
            'image': ''
        }
        res = self.client.post(PRODUCTS_URL, product)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_success(self):
        """Test update Product is successful"""
        product = sample_product(supplier_id=self.user, name='old-name', price='100.00')
        url = detail_url(product.id)
        new_product = {
            'name': 'new_name',
            'price': '1000.0',
            'image': ''
        }
        res = self.client.put(url, new_product)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], new_product['name'])

    def test_delete_store_success(self):
        """Test delete Product is successful"""
        product = sample_product(supplier_id=self.user)
        url = detail_url(product.id)
        res = self.client.delete(url)
        products = Product.objects.all()

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(products), 0)
