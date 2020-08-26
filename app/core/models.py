from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    """Create and save a new user"""

    def create_user(self, email, user_type, password=None, **extra_fields):
        """Create and save a new user"""
        if not email:
            raise ValueError('User must have a valid email address.')

        allowed_values = ['Supplier', 'Customer', 'Admin']
        if user_type not in allowed_values:
            raise ValueError('User type Must be either a Customer or a Supplier.')

        user = self.model(email=email.lower(), user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creates and saves a new superuser"""
        user = self.create_user(email, 'Admin', password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


# TODO: remove is_superuser, is_staff, is_active property
# TODO: refactor create_user, create_superuser when user_type is supplied
class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_type = models.CharField(max_length=10)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Store(models.Model):
    """Store Model"""
    name = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=25)
    cash = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.city} - {self.name}'


class Product(models.Model):
    """product Model"""
    supplier_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Transaction(models.Model):
    """Transaction Model"""
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='admin_user')
    party = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='party_user')
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    trx_type = models.CharField(max_length=10)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)


class TransactionProduct(models.Model):
    """TransactionProduct Model"""
    trx_id = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class StoreProduct(models.Model):
    """StoreProduct Model"""
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

