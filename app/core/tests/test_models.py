from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models

class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email and password"""
        email = 'user@user.com'
        password = 'user123'
        user_type = 'Supplier'
        user = get_user_model().objects.create_user(email, user_type, password)

        self.assertEqual(user.email, email)
        self.assertEqual(user.user_type, user_type)
        self.assertTrue(user.check_password(password))


    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'uSer@USER.com'

        user = get_user_model().objects.create_user(email, 'Customer', 'user123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating a user without email raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Supplier', 'test123')

    def test_new_user_invalid_type(self):
        """Test creating a user with invalid type raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('test@test.com', 'Not_Supplier', 'test123')


    def test_store_str(self):
        """Test the store string representation"""
        store = models.Store.objects.create(
            city='Cairo',
            name='Store#1'
        )

        self.assertEqual(str(store), 'Cairo - Store#1')
        self.assertEqual(store.cash, 0)