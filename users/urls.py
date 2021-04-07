from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import UserViewSet, TokenViewSet

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
