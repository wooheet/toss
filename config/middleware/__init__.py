import logging
import re

from django.conf import settings
from django.http import JsonResponse

from config.log import LOG

logger = logging.getLogger(__name__)

REG_VER_NO = r'[a-zA-Z0-9._;\(\)\+\- ]+'
REG_UA_PREFIX = r'(Toss|Apache-HttpClient|TOssWebServer|nginx-rtmp)'
REG_UA_MODULE = r'(nginx|requests|WebServer|AuthServer'\
                r'|Dalvik|CFNetwork|\(Java)\/[a-zA-Z0-9._;\(\)\+\- ]+'


REG_UA_GENERAL = re.compile(
    f'{REG_UA_PREFIX}\/{REG_VER_NO} {REG_UA_MODULE}')
REG_UA_EXCEPTIONAL = re.compile(
    f'Toss\/{REG_VER_NO} Mozilla\/{REG_VER_NO}\(Linux; Android {REG_VER_NO}')

ALLOWED_USER_AGENTS = [
    REG_UA_GENERAL,
    REG_UA_EXCEPTIONAL
]

BLACK_LIST_AGENTS = [
    re.compile(f'Toss\/{REG_VER_NO}Dalvik\/{REG_VER_NO}\(Linux{REG_VER_NO}Android{REG_VER_NO}G011A Build\/LMY48Z\)')
]


class NotTrustUAException(Exception):
    pass


def search_agent(regex_list, user_agent):
    for _regex in regex_list:
        if _regex.search(user_agent):
            return True
    return False


def black_list(user_agent):
    return search_agent(regex_list=BLACK_LIST_AGENTS, user_agent=user_agent)


def allowed_agent(user_agent):
    return search_agent(regex_list=ALLOWED_USER_AGENTS, user_agent=user_agent)


def allowed_referer(referer):
    try:
        # Web or Others
        # for site in TRUSTED_SITES:
        #     if site in referer:
        #         break
        # else:
        #     logger.warning(f'Invalid Referer : {referer}')
        #     raise NotTrustUAException()
        pass
    except KeyError:
        raise NotTrustUAException()


class UAValidateMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        try:
            try:
                _user_agent = request.META["HTTP_USER_AGENT"]
            except KeyError:
                logger.warning("UA header doesn't exists.")
                raise NotTrustUAException()

            if black_list(user_agent=_user_agent):
                raise NotTrustUAException()

            if not allowed_agent(user_agent=_user_agent):
                allowed_referer(referer=request.META.get("HTTP_REFERER", ""))

        except NotTrustUAException:
            logger.warning(f'NotTrustUAException : '
                           f'{request.META.get("HTTP_USER_AGENT")}, '
                           f'{request.META.get("HTTP_REFERER")}')

            LOG(event='UNAUTHORIZED_AGENT_DETECT', request=request)

        return self.get_response(request)


def get_maintenance_response():
    # 실제 HTTP스펙의 상태코드
    http_status_code = settings.MAINTENANCE_HTTP_STATUS_CODE

    # Response body안에 status 필드의 값
    status = settings.MAINTENANCE_STATUS

    # 제목
    subject = settings.MAINTENANCE_SUBJECT

    # 본문
    contents = settings.MAINTENANCE_CONTENTS

    if subject is None or contents is None:
        msg ='The environment variables MAINTENANCE_SUBJECT and ' \
             'MAINTENANCE_CONTENTS are incorrect, so Maintenance Middleware ' \
             'does not work properly.'
        raise ServerMaintenanceMiddleware.NotWorkingError(msg)

    return JsonResponse(
        dict(
            status=status,
            subject=subject,
            contents=contents
        ),
        status=http_status_code
    )


class ServerMaintenanceMiddleware:

    class NotWorkingError(Exception):
        pass

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        try:
            if 'health' not in request.path:
                return get_maintenance_response()
        except Exception as e:
            logger.error(e, exc_info=True)
        return self.get_response(request)

