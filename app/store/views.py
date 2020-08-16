from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser

from core.models import Store

from store import serializers



class StoreViewSet(viewsets.ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)
    queryset = Store.objects.all()
    serializer_class = serializers.StoreSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        return self.queryset.order_by('-name')
