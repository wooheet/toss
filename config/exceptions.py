from rest_framework import exceptions
from rest_framework.exceptions import (ValidationError, ParseError,
                                       AuthenticationFailed, NotAuthenticated,
                                       PermissionDenied, NotFound,
                                       MethodNotAllowed, NotAcceptable,
                                       UnsupportedMediaType, Throttled)

HTTP_460_JWT_TOKEN_EXPIRE = 460
HTTP_500_JWT_TOKEN_SERVER_ERROR = 500


class AuthJWTTokenExpired(exceptions.APIException):
    status_code = HTTP_460_JWT_TOKEN_EXPIRE
    default_detail = exceptions._('Auth JWT Token Expired.')
    default_code = 'auth_jwt_token_expired'


class AuthJWTTokenServerError(exceptions.APIException):
    status_code = HTTP_500_JWT_TOKEN_SERVER_ERROR
    default_detail = exceptions._('Auth JWT Token Server Error.')
    default_code = 'auth_jwt_token_server_error'
