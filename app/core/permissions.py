from rest_framework.permissions import BasePermission

from django.contrib.auth import get_user_model


allowed_types = ['Supplier', 'Admin']

class IsAuthenticatedOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'GET':
            return True

        user = get_user_model().objects.get(email=request.user)
        if  request.user and user.is_authenticated and user.user_type in allowed_types:
            return True
        return False