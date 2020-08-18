from django.urls import path, include
from rest_framework.routers import DefaultRouter

from transaction import views

router = DefaultRouter()
router.register('my-transactions', views.MyTransactionViewSet)
router.register('', views.TransactionViewSet)

app_name = 'transaction'

urlpatterns = [
    path('', include(router.urls)),
]