from enum import Enum
from rest_framework.views import exception_handler


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.value, x.name) for x in cls)

    @classmethod
    def get_values(cls):
        return[x.value for x in cls]

    @classmethod
    def get_keys(cls):
        return [x.name for x in cls]


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code
    return response