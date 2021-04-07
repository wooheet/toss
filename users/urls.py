from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import UserViewSet, TokenViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='user')
router.register(r'token', TokenViewSet, basename='token')
router.register(r'token/refresh', TokenViewSet, basename='token-refresh')

urlpatterns = [
    path('', include(router.urls)),
]
