import copy
import logging
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, mixins, views
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User, Profile
from .serializers import (UserSerializer, MyProfileSerializer, \
                          UserLoginAndSignResultSerializer)
from config.mixins import CustomResponseMixin, CustomPaginatorMixin
from django.http import HttpResponse
from config.log import LOG

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

            # Auth SignUp 절차가 완료되지 않았다.
            # if login_user.user_signin_status_check_and_fix():
            #     result = get_login_result_message(
            #         result_code=AUTH_NOT_FOUND)
            #     return self.success(results=result)

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

    @action(detail=False, methods=['get'])
    def get_tokens(request: GetTokenReq, meta: Dict = Depends(get_meta)):
        """JWT와 Refresh Token을 반환한다."""
        try:
            # Validator를 통해 profile 정보를 가지고 온다.
            # request body 의 auth_data 로 VALIDATOR_DICT 에 매칭이되는 인스턴스를 가져옴
            act_validator = AccountValidatorFactory.get_instance(request.auth_data)
            profile, act_data = await get_account_profile(act_validator)

            # 이미 가임된 계정이 아님을 확인하기 위해 계정을 조회한다.
            account_item = await AccountTable.get(
                profile['act_type'], profile['act_id']
            )

            # [TEMP]: 마이그레이션 실패 방어코드
            # AccountTable 에서 얻어온 정보가 None 이면 RDS 에서 동기화 시도
            account_item = await check_legacy_account(account_item, profile)

            # 계정이 존재하지 않는 경우
            if account_item is None:
                act_validator.verify_create()
                user_data = await ApiInterface.create_user(
                    profile['act_type'], profile['act_id'],
                    request.device_unique_id, profile
                )

                if user_data.status == AccountStatus.BANNED:
                    return error_rsp(
                        ErrorCode.LimitedUser, data=user_data.data
                    )

                user_id = user_data.user_id

                await AccountTable.create(
                    profile['act_type'], profile['act_id'], user_id,
                    act_data, profile
                )

            # 계정이 존재하는 경우
            else:
                user_id = account_item['user_id']

                # [TEMP]: 마이그레이션 실패 방어코드
                user_status_data = await ApiInterface.get_user_status(
                    user_id, request.device_unique_id
                )

                if check_sync_status(account_item, user_status_data):
                    await AccountTable.sync_status(
                        [account_item], user_status_data.status,
                        user_status_data.updated
                    )
                    # 상태를 동기화 시킨 후 account_item을 새로 가지고 온다.
                    account_item = await AccountTable.get(
                        profile['act_type'], profile['act_id']
                    )

                # 정지 상태 유저
                if user_status_data.status == AccountStatus.BANNED:
                    return error_rsp(
                        ErrorCode.LimitedUser, data=user_status_data.data
                    )
                # 7일이 지나지 않은 탈퇴 상태인 경우
                elif account_item['status'] == AccountStatus.LEAVED:
                    return error_rsp(ErrorCode.NotRejoinableAccount)

                # 정상적인 계정이 존재하는 경우
                #
                act_validator.verify(
                    account_item.get('act_data', {}),
                    user_status_data.status
                )

        except AuthError as e:
            # TODO: Error from AccountValidatorFactory
            if type(e) == AuthAlreadyExistAccount:
                await AccountTable.recovery_abandoned_account(
                    account_item['act_type'], account_item['act_id']
                )
                return error_rsp(ErrorCode.AlreadyExistAccount)
            elif type(e) == AuthDoestNotExistAccount:
                return error_rsp(ErrorCode.DoesNotExistAccount)

            return error_rsp(ErrorCode.InvalidExternalToken)

        except InvalidIdPassword:
            return error_rsp(ErrorCode.InvalidIdPassword)

        except AlreadyExistAccount:
            return error_rsp(ErrorCode.AlreadyExistAccount)

        except ApiInterfaceError as e:
            if type(e) == ApiInterfaceDoesNotExist:
                return error_rsp(ErrorCode.DoesNotExistAccount)
            return error_rsp(ErrorCode.InternalServiceError)

        # 토큰을 생성한다.
        jwt = JwtManager.create_jwt(user_id, request.device_unique_id)
        refresh_token = JwtManager.create_refresh_token()
        await RefreshTokenTable.create(
            user_id, request.device_unique_id, refresh_token
        )

        return GetTokenRsp(data={'jwt': jwt, 'refresh_token': refresh_token})


    @action(detail=False, methods=['get'])
    def refresh_token(request: RefreshTokenReq, meta: Dict = Depends(get_meta)):
        """Refresh Token을 활용하여 JWT와 Refresh Token을 갱신한다."""
        try:
            # JWT 갱신 시, Refresh Token도 함께 갱신하다.
            await RefreshTokenTable.renew_and_get(
                request.user_id, request.device_unique_id, request.refresh_token
            )

            user_status_data = await ApiInterface.get_user_status(
                request.user_id, request.device_unique_id
            )

            # 유저 계정 정지 상태를 확인한다.
            # Normal 상태는 0(LogOut), 1(LogIn) 포함해서 0 이라고 정의
            if user_status_data.status != AccountStatus.NORMAL:
                return error_rsp(ErrorCode.LeavedOrLimitedUser)

        except DoesNotExistRefreshToken:
            return error_rsp(ErrorCode.ExpiredRefreshToken)

        except ApiInterfaceError as e:
            if type(e) == ApiInterfaceDoesNotExist:
                return error_rsp(ErrorCode.DoesNotExistAccount)
            return error_rsp(ErrorCode.InternalServiceError)

        # 유효 하다면 jwt를 생성하여 응답한다.
        jwt = JwtManager.create_jwt(request.user_id, request.device_unique_id)
        return RefreshTokenRsp(data={'jwt': jwt})
