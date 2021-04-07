import copy
import logging
from rest_framework import viewsets, mixins, views
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Profile
from .serializers import (UserSerializer, MyProfileSerializer, \
                          UserLoginAndSignResultSerializer)
from config.mixins import CustomResponseMixin, CustomPaginatorMixin
from config.log import LOG
from config.manager import TokenManager

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet,
                  CustomResponseMixin,
                  CustomPaginatorMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
             Auth Server 사용자 가입 Pnd SignUp API
             Pre validation check
         ---
         responseMessages:
             -   code:   200
                 message: SUCCESS
             -   code:   400
                 message: BADREQUEST
             -   code:   403
                 message: FORBIDDEN. (제재, 차단 사용자)
             -   code:   409
                 message: CONFLICT. (이미 가입된 사용자가 존재함)
             -   code:   500
                 message: SERVER ERROR
         """

        try:
            data_copy = copy.deepcopy(request.data)
            LOG(request=request, event='USER_NEW_SIGN_PND',
                data=dict(extra=data_copy))

            params = request.data.get('profile', None)

            if params:
                pnd_signup_user = User.pre_signup(params)

                data = {
                    'user_id': pnd_signup_user.id
                }

            else:
                logger.error('No Auth Server', exc_info=True)
                return self.bad_request()

        except Exception as e:
            logger.error(e, exc_info=True)
            return self.server_exception()

        return self.success(results=data)

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


class SignUpView(views.APIView, CustomResponseMixin):
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
            LOG(request=request, event='USER_SIGN', data=dict(extra=data_copy))

            profile = user.profile

            profile = Profile(
                nickname=profile.nickname,
            )

            signup_user = User.post_signup(request)

            serializer = UserLoginAndSignResultSerializer(signup_user)

        except Exception as e:
            return self.server_exception()

        return self.success(results=serializer.data)


class SignInView(views.APIView, CustomResponseMixin):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):

        """
            New 사용자 SignIn API 사용자 가입 여부 확인 및 가입 정보 전달
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
                message: BAD REQUEST. (파라미터가 유효하지 않음)
            -   code:   403
                message: FORBIDDEN. (제재 사용자)
            -   code:   500
                message: SERVER ERROR
        """
        try:

            data_copy = copy.deepcopy(request.data)
            LOG(request=request, event='USER_LOGIN',
                data=dict(extra=data_copy))

            login_user = request.user

            if not login_user.is_authenticated:
                return self.un_authorized()

            user_data = UserLoginAndSignResultSerializer(login_user).data

        except ValueError as e:
            logger.error(e, exc_info=True)
            return self.bad_request()

        except Exception as e:
            logger.error(e, exc_info=True)
            return self.server_exception()

        LOG(request=request, event='USER_LOGIN_COMPLETE',
            data=dict(extra=data_copy))
        return self.success(results=user_data)


class TokenViewSet(views.APIView, CustomResponseMixin):
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        data = dict()

        try:
            user_id = request.user.id
            device_unique_id = request.data.get('device_unique_id',
                                                'device_unique_id')

            token_manager = TokenManager()

            token = token_manager.create_jwt(user_id, device_unique_id)
            refresh_token = token_manager.create_refresh_token()

            data = {
                'token': token,
                'refresh_token': refresh_token
            }
        except Exception as e:
            logger.error(e)

        return self.success(results=data)
