from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.validators import validate_slug
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from apps.core.models import App, Purchase
from apps.core.serializers import AppReadSerializer, UploadedIconSerializer, AppCreateSerializer, \
    AppUpdateSerializer, PurchaseReadSerializer, PurchaseWriteSerializer


class PaginatorMixin:
    def paginate(self, qs, request, serializer_class):
        paginator = PageNumberPagination()
        paginated_qs = paginator.paginate_queryset(qs, request)
        serializer = serializer_class(paginated_qs, many=True)
        return paginator.get_paginated_response(serializer.data)


class AppViewsets(viewsets.ViewSet, PaginatorMixin):
    def list(self, request):
        qs = App.objects.filter(user=self.request.user)
        return self.paginate(qs, request, AppReadSerializer)

    def retrieve(self, request, pk=None):
        qs = App.objects.filter(pk=pk, user=self.request.user)
        user = get_object_or_404(qs, pk=pk)
        serializer = AppReadSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        request.data['user'] = self.request.user.id
        serializer = AppCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        return self.do_update(pk, is_partial=False)

    def partial_update(self, request, pk=None):
        return self.do_update(pk, is_partial=True)

    def destroy(self, request, pk=None):
        qs = App.objects.filter(pk=pk, user=self.request.user)
        user = get_object_or_404(qs, pk=pk)
        user.delete()
        return Response(status=status.HTTP_200_OK)

    def do_update(self, pk, is_partial):
        qs = App.objects.filter(pk=pk, user=self.request.user)
        user = get_object_or_404(qs, pk=pk)
        serializer = AppUpdateSerializer(data=self.request.data, instance=user, partial=is_partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK, data=AppReadSerializer(instance=user).data)


class VerifiedAppsView(generics.ListAPIView):
    serializer_class = AppReadSerializer

    def get_queryset(self):
        qs = App.objects.filter(verified=True).exclude(user=self.request.user.id)
        search_param = self.request.GET.get('search')

        try:
            validate_slug(search_param)
            if search_param:
                qs = qs.filter(
                    Q(title__icontains=search_param) | Q(description__icontains=search_param)
                )
        except ValidationError:
            pass

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['scope'] = 'public'
        return context


class PurchaseViewsets(viewsets.ViewSet, PaginatorMixin):
    def list(self, request):
        qs = Purchase.objects.filter(issued_by=self.request.user).select_related('app')
        return self.paginate(qs, request, PurchaseReadSerializer)

    def retrieve(self, request, pk=None):
        qs = Purchase.objects.filter(pk=pk, issued_by=self.request.user).select_related('app')
        obj = get_object_or_404(qs, pk=pk)
        serializer = PurchaseReadSerializer(obj)
        return Response(serializer.data)

    def create(self, request):
        request.data['issued_by'] = self.request.user.id
        serializer = PurchaseWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase = serializer.save()
        return Response(status=status.HTTP_200_OK, data=AppReadSerializer(instance=purchase.app).data)


class Upload(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        serializer = UploadedIconSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

