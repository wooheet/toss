import logging
from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import CursorPagination
from rest_framework.utils.serializer_helpers import ReturnList


logger = logging.getLogger(__name__)


class CustomCursorPagination(CursorPagination):

    def __init__(self, request=None, ordering=None, page_size=None):
        if request:
            if page_size is None:
                self.page_size = int(request.query_params.get('page_size', 30))
            else:
                self.page_size = page_size

            if self.page_size > 30:
                logger.warning('illegal page_size : {}'.format(self.page_size))
                self.page_size = 30

        if ordering:
            self.ordering = ordering

    def _next_link(self):
        next_link = None
        try:
            next_link = self.get_next_link()
        except (IndexError, AttributeError):
            pass
        except Exception as e:
            logger.error(e)
        return next_link or ''

    def _previous_link(self):
        previous_link = None
        try:
            previous_link = self.get_previous_link()
        except (IndexError, AttributeError):
            pass
        except Exception as e:
            logger.error(e)
        return previous_link or ''

    def get_paginated_response(self, data, args=[]):
        if type(data) != ReturnList and type(data) != list:
            results = [data]
        else:
            results = data
        return Response(OrderedDict([
            ('status_code', '200'),
            ('detail', 'Success'),
            ('next', self._next_link()),
            ('previous', self._previous_link()),
            ('results', results),
            *args
        ]))

    def get_paginated_response_without_status_code(self,
                                                   data,
                                                   replace_from_url=None,
                                                   replace_to_url=None):

        if type(data) != ReturnList and type(data) != list:
            results = [data]
        else:
            results = data

        next_url = self._next_link()
        previous_url = self._previous_link()
        if replace_from_url is not None and replace_to_url is not None:
            next_url = next_url.replace(replace_from_url, replace_to_url)
            previous_url = previous_url.replace(replace_from_url,
                                                replace_to_url)

        return dict(next=next_url, previous=previous_url, results=results)