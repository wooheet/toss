import logging

import jwt

from config import settings, exceptions as toss_exception
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import (TokenAuthentication,
                                           get_authorization_header)
from users.models import User

logger = logging.getLogger(__name__)


class CustomTokenAuthentication(TokenAuthentication):

    def authenticate_credentials(self, key):
        model = self.get_model()

        try:
            queryset = model.objects.prefetch_related('user')
            token = queryset.get(key=key)

        except model.DoesNotExist:
            try:
                logger.warning("Invalid Token : {}".format(key))
            except exceptions:
                logger.exception('Invalid Key Info')

            raise toss_exception.AuthenticationFailed(_('Invalid token.'))

        if token.user.status < 0:
            raise toss_exception.AuthenticationFailed(_('User inactive or deleted.'))

        return token.user, token


class CustomJwtTokenAuthentication(TokenAuthentication):

    keyword = 'Bearer'
    ALLOW_PND_USER_APIS = ['signup', 'signin']

    def __init__(self):
        self.user = User.objects.get(id=self.user_id)

    def get_path_info(self, request):
        path_info = request.META.get('PATH_INFO', None)
        if path_info is not None:
            path_info = path_info.replace('/', '')
        return path_info

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = \
            _('Invalid token header. Token string should not contain spaces.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError:
            msg = \
            _('Invalid token header. Token string should not contain invalid characters.')
            raise exceptions.AuthenticationFailed(msg);

        self.path_info = self.get_path_info(request)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, key):
        try:
            res = self._jwt_token_validator(key)
            self.user_id = res.get('sub')
            self.device_unique_id = res.get('did', None)
            self.exp = res.get('exp', None)

            if self.exp is None:
                logger.warning("No exp in token.")
                self._error_log(key)
                raise toss_exception.AuthenticationFailed('No exp in token.')

        except jwt.ExpiredSignatureError:
            logger.warning("Expired token.")
            self._error_log(key)
            raise toss_exception.AuthJWTTokenExpired(_('Expired token.'))
        except jwt.InvalidTokenError:
            logger.warning("Invalid Token.")
            self._error_log(key)
            raise toss_exception.AuthenticationFailed('Invalid token.')
        except Exception as e:
            logger.error(f'key {key} e {e}', exc_info=True)
            raise toss_exception.AuthJWTTokenServerError(_('Exceptions.'))

        # if self.user.status == User.Status.LEAVED.value:
        #     raise toss_exception.AuthenticationFailed(
        #         _('User inactive or deleted.'))
        # elif self.user.status == User.Status.BANNED.value:
        #     raise toss_exception.AuthenticationFailed(
        #         _('User banned.'))
        # elif self.user.status == User.Status.SIGNUP_PND.value:
        #     if self.path_info not in CustomJwtTokenAuthentication.ALLOW_PND_USER_APIS:
        #         raise toss_exception.AuthenticationFailed(
        #         _('Not allowed pnd user.'))

        return self.user, None

    def _error_log(self, key):
        res = self._jwt_token_validator(key, verify=False)
        log = f'token : {key} \n'
        log += f'user_id : {res.get("sub")} \n'
        log += f'did : {res.get("did", None)} \n'
        log += f'exp : {res.get("exp", None)}'
        logger.warning(log)

    def _jwt_token_validator(self, key, verify=True):
        return jwt.decode(key, settings.AUTH_SERVER_PUB_KEY,
                          algorithms=['RS256'], verify=verify)

