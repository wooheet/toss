from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username', 'password']


class MyProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields ='__all__'