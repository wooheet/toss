from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import UserViewSet, SignUpView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'signup', SignUpView, basename='signup')

urlpatterns = [
    path('', include(router.urls)),
]
