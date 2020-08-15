from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db import models


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
