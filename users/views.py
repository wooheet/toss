import copy
from django.shortcuts import render
from rest_framework import viewsets, mixins, views
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import (UserSerializer, MyProfileSerializer, \
                          UserLoginAndSignResultSerializer)
from config.mixins import CustomResponseMixin, CustomPaginatorMixin
from django.http import HttpResponse


class UserViewSet(viewsets.ModelViewSet,
                  CustomResponseMixin,
                  CustomPaginatorMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):

        return self.success()

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
        print(request.user)
        if not request.user.is_authenticated:
            return self.un_authorized()

        serializer = MyProfileSerializer(
            request.user, context=dict(request=request)
        )
        return self.success(results=serializer.data)

    @action(detail=False, methods=['get'])
    def index(self, request, *args, **kwargs):
        return HttpResponse("Hello, world. You're at the polls index.")


class SignUpView(viewsets.ModelViewSet,
                 CustomResponseMixin,
                 CustomPaginatorMixin):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, format=None):
        """
            New 사용자 가입 SignUp API
        ---
        response_serializer: users.serializers.UserLoginAndSignResultSerializer
        parameters:
            - name: body
              pytype: users.serializers.UserIdTokenLoginSerializer
              paramType: body
        responseMessages:
            -   code:   200
                message: SUCCESS
            -   code:   400
                message: BADREQUEST.
            -   code:   403
                message: FORBIDDEN.
            -   code:   409
                message: CONFLICT.
            -   code:   500
                message: SERVER ERROR
        """

        try:
            user = request.user

            if not user.is_authenticated:
                return self.un_authorized()

            data_copy = copy.deepcopy(request.data)

            serializer = UserLoginAndSignResultSerializer(
                context=dict(request=request)
            )

        except Exception as e:
            return self.server_exception()

        return self.success(results=serializer.data)
