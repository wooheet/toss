from django.shortcuts import render
from rest_framework import viewsets, mixins, views
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserSerializer, MyProfileSerializer
from config.mixins import CustomResponseMixin, CustomPaginatorMixin


class UserViewSet(viewsets.ModelViewSet,
                  CustomResponseMixin,
                  CustomPaginatorMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['get'])
    def me(self, request, *args, **kwargs):
        """
            본인 Profile 조회 API
        ---
        response_serializer: users.serializers.MyProfileSerializer
        parameters:
            -   name: pk
                description : Profile 정보를 조회 할 User ID
                paramType: path
        responseMessages:
            -   code:   200
                message: SUCCESS
            -   code:   404
                message: NOT FOUND
            -   code:   500
                message: SERVER ERROR
        """
        if not request.user.is_authenticated:
            return self.un_authorized()

        serializer = MyProfileSerializer(
            request.user, context=dict(request=request)
        )
        return self.success(results=serializer.data)