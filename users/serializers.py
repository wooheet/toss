from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import User


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = '__all__'
		extra_kwargs = {'password': {'write_only': True, 'required': True}}

	def create(self, validated_data):
		user = User.objects.create_user(**validated_data)
		Token.objects.create(user=user)
		return user


class MyProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields ='__all__'


class UserLoginAndSignResultSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields ='__all__'