import logging
from django.conf import settings
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param
from rest_framework.utils.serializer_helpers import ReturnList
from .pagenation import CustomCursorPagination

logger = logging.getLogger(__name__)


class CustomResponseMixin(object):

    def _validation_error(self, error):
        if isinstance(error, dict) and 'code' in error and 'message' in error:
            return True
        return False

    def success(self, status_code=200, detail='Success', results=None,
                next=None, previous=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, next=next, previous=previous)

    def bad_request(self, status_code=400, detail="Bad Request", results=None,
                    error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def forbidden(self, status_code=403, detail="Forbidden", results=None,
                  error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def not_acceptable(self, status_code=406, detail="Not Acceptable",
                       results=None, error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def not_found(self, status_code=404, detail="Not Found", results=None,
                  error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def timeout(self, status_code=408, detail="Request Time Out",
                results=None, error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def server_maintenance(self, status_code=503, detail="Server Maintenance",
                           results=None, error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def server_exception(self, status_code=500,
                         detail="Iternal Server Exception", results=None,
                         error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def un_authorized(self, status_code=401, detail="UnAuthorized Request",
                      results=None, error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def conflict(self, status_code=409, detail="Conflict", results=None,
                 error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def unprocessable_entity(self, status_code=422,
                             detail="Unprocessable Entity", results=None,
                             error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def too_many_request(self, status_code=429, detail="Too Many Requests",
                         results=None, error=None):
        return self.get_response(status_code=status_code, detail=detail,
                                 results=results, error=error)

    def get_response(self, status_code, detail, results, next=None,
                     previous=None, error=None):
        if results is None:
            results = []

        if type(results) != ReturnList and type(results) != list:
            results = [results]

        data = {'status_code': status_code, 'detail': u'{}'.format(detail),
                'results': results}

        if error and isinstance(error, dict) and 'code' in error \
                and 'message' in error:
            data['error'] = error

        if next is not None or previous is not None:
            data["next"] = next or ""
            data["previous"] = previous or ""

        return Response(status=status_code, data=data)


class CustomPaginatorMixin(object):

    def get_page_response_with_args(self, request=None, queryset=None,
                                    serializer=None, ordering='-created',
                                    page_size=None, context=None, args=[]):
        if context is None:
            context = {}
        paginator = CustomCursorPagination(request=request, ordering=ordering,
                                           page_size=page_size)
        page_queryset = paginator.paginate_queryset(request=request,
                                                    queryset=queryset)
        page_serializer = serializer(page_queryset, many=True, context=context)
        return paginator.get_paginated_response(data=page_serializer.data,
                                                args=args)

    def get_page_response(self, request=None, queryset=None, serializer=None,
                          ordering='-created', page_size=None, context=None):
        if context is None:
            context = {}
        paginator = CustomCursorPagination(request=request, ordering=ordering,
                                           page_size=page_size)
        page_queryset = paginator.paginate_queryset(request=request,
                                                    queryset=queryset)
        page_serializer = serializer(page_queryset, many=True, context=context)
        return paginator.get_paginated_response(data=page_serializer.data)


    def get_page_response_without_status_code(self, request=None,
                                              queryset=None, serializer=None,
                                              replace_from_url=None,
                                              replace_to_url=None,
                                              page_size=None,
                                              ordering='-created',
                                              context=None):

        try:
            if context is None:
                context = {}
            paginator = CustomCursorPagination(request=request,
                                               ordering=ordering,
                                               page_size=page_size)
            page_queryset = paginator.paginate_queryset(request=request,
                                                        queryset=queryset)
            page_serializer = serializer(page_queryset, many=True,
                                         context=context)
            res = paginator.get_paginated_response_without_status_code(
                data=page_serializer.data,
                replace_from_url=replace_from_url,
                replace_to_url=replace_to_url
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            res = dict(next="", previous="", results=[])
        return res

    def build_page_link(self, cursor, cursor_query_param='cursor'):
        if cursor is None:
            return ''

        base_uri = self.request.build_absolute_uri()
        return replace_query_param(base_uri, cursor_query_param, cursor)