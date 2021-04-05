from __future__ import absolute_import

import logging
import json
import os

from django.utils import timezone
from django.conf import settings
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION
from django.contrib.contenttypes.models import ContentType
from django.core.handlers.wsgi import WSGIRequest

logger = logging.getLogger(settings.ACTION_LOGGER_NAME)

private_set = {'password', 'refund_account', 'refund_bank', 'refund_name',
               'depositor', 'email', 'phone_number', 'new_password'}


def LOG_ENTRY_DELETION(request, object, object_repr, action_flag=DELETION):
    LOG_ENTRY(request, object, object_repr, action_flag)


def LOG_ENTRY_ADDITION(request, object, object_repr, action_flag=ADDITION):
    LOG_ENTRY(request, object, object_repr, action_flag)


def LOG_ENTRY_CHANGE(request, object, object_repr, action_flag=CHANGE):
    LOG_ENTRY(request, object, object_repr, action_flag)


def LOG_ENTRY(request, object, object_repr, action_flag):
    LogEntry.objects.log_action(
        user_id=request.user.id,
        content_type_id=ContentType.objects.get_for_model(object).pk,
        object_id=object.id,
        object_repr=object_repr,
        action_flag=action_flag
    )


def get_safe_extra_data(data):
    if data and 'extra' in data:
        extra_data = data.get('extra')
        safe_extra_data = dict(filter(
            lambda x: x[0] not in private_set, extra_data.items()
        ))
    else:
        safe_extra_data = None
    return safe_extra_data


def get_log_data(event, request):
    return dict(event=event,
                client_ip=request.META.get(
                    'HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR'),
                agent=request.META.get('HTTP_USER_AGENT'),
                time=timezone.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                server_release=os.getenv('SENTRY_RELEASE') or '')


def set_user_data(user, log_data):
    log_data['user_id'] = user.id
    if hasattr(user, 'account'):
        log_data['sns_type'] = user.account.sns_type
        log_data['sns_id'] = user.account.sns_id

    if hasattr(user, 'profile'):
        log_data['user_nickname'] = user.profile.nickname
        log_data['user_tag'] = user.profile.tag


def LOG(request, event, data=None):
    try:

        log_data = get_log_data(event=event, request=request)
        if data is None:
            data = dict()

        data['path'] = request.path
        data['referer'] = request.META.get('HTTP_REFERER')

        if not isinstance(request, WSGIRequest):
            data['extra'] = get_safe_extra_data(data)
            if request.user.is_authenticated:
                set_user_data(user=request.user, log_data=log_data)

        log_data['data'] = data
        logger.info(json.dumps(log_data, ensure_ascii=False))

    except Exception as e:
        logger.error(e, exc_info=True)
        log_data = None

    return log_data
