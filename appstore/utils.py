from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from drf_yasg import openapi


class CustomSchemes:
    user = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING),
            "email": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
        },
        required=[]
    )

    token_pair = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "refresh": openapi.Schema(type=openapi.TYPE_STRING),
            "access": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=[]
    )

    error = openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "detail": openapi.Schema(type=openapi.TYPE_STRING)
        }
    )


class PaginatorMixin:
    def paginate(self, qs, request, serializer_class):
        paginator = PageNumberPagination()
        paginator.page_size = settings.PAGE_SIZE
        paginated_qs = paginator.paginate_queryset(qs, request)
        serializer = serializer_class(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)