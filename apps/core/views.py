from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.core.validators import validate_slug
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.core.models import App, Purchase
from apps.core.serializers import AppReadSerializer, UploadedIconSerializer, AppCreateSerializer, \
    AppUpdateSerializer, PurchaseReadSerializer, PurchaseWriteSerializer, AppPaginationSerializer, \
    VerifiedPaginationSerializer, PurchasePaginationSerializer
from appstore.utils import CustomSchemes, PaginatorMixin


class AppViewsets(viewsets.ViewSet, PaginatorMixin):
    @swagger_auto_schema(
        operation_description="Paginated list of user created apps",
        responses={
            status.HTTP_200_OK: AppPaginationSerializer
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='int', description='Number of page', required=False)
        ],
        operation_id="apps"
    )
    def list(self, request):
        qs = App.objects.filter(user=self.request.user)
        return self.paginate(qs, request, AppReadSerializer)

    @swagger_auto_schema(
        operation_description="Retrieve the app",
        responses={
            status.HTTP_200_OK: AppReadSerializer,
            status.HTTP_404_NOT_FOUND: CustomSchemes.error
        },
        operation_id="retrieve app"
    )
    def retrieve(self, request, pk=None):
        qs = App.objects.filter(pk=pk, user=self.request.user)
        user = get_object_or_404(qs, pk=pk)
        serializer = AppReadSerializer(user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create new app",
        responses={
            status.HTTP_201_CREATED: AppReadSerializer
        },
        operation_id="create app"
    )
    def create(self, request):
        request.data['user'] = self.request.user.id
        serializer = AppCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        app = serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=AppReadSerializer(instance=app).data)

    @swagger_auto_schema(
        operation_description="Full update of the app",
        responses={
            status.HTTP_200_OK: AppReadSerializer
        },
        operation_id="put app"
    )
    def update(self, request, pk=None):
        return self.do_update(pk, is_partial=False)

    @swagger_auto_schema(
        operation_description="Partial update of the app",
        responses={
            status.HTTP_200_OK: AppReadSerializer
        },
        operation_id="patch app"
    )
    def partial_update(self, request, pk=None):
        return self.do_update(pk, is_partial=True)

    @swagger_auto_schema(
        operation_description="Delete the app",
        operation_id="delete app"
    )
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

    @swagger_auto_schema(
        operation_description="Paginated list of verified apps",
        responses={
            status.HTTP_200_OK: VerifiedPaginationSerializer
        },
        operation_id="verified apps"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
    @swagger_auto_schema(
        operation_description="Paginated list of purchased apps",
        responses={
            status.HTTP_200_OK: PurchasePaginationSerializer
        },
        manual_parameters=[
            openapi.Parameter('page', openapi.IN_QUERY, type='int', description='Number of page', required=False)
        ],
        operation_id="purchased apps"
    )
    def list(self, request):
        qs = Purchase.objects.filter(issued_by=self.request.user).select_related('app')
        return self.paginate(qs, request, PurchaseReadSerializer)

    @swagger_auto_schema(
        operation_description="Retrieve the purchase detail",
        responses={
            status.HTTP_200_OK: PurchaseReadSerializer,
            status.HTTP_404_NOT_FOUND: CustomSchemes.error,
            status.HTTP_400_BAD_REQUEST: CustomSchemes.error
        },
        operation_id="retrieve purchase"
    )
    def retrieve(self, request, pk=None):
        qs = Purchase.objects.filter(pk=pk, issued_by=self.request.user).select_related('app')
        obj = get_object_or_404(qs, pk=pk)
        serializer = PurchaseReadSerializer(obj)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Purchase an app",
        responses={
            status.HTTP_200_OK: PurchaseReadSerializer,
        },
        operation_id="purchase app"
    )
    def create(self, request):
        request.data['issued_by'] = self.request.user.id
        serializer = PurchaseWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        purchase = serializer.save()
        return Response(status=status.HTTP_200_OK, data=AppReadSerializer(instance=purchase.app).data)


class Upload(APIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Upload an icon",
        responses={
            status.HTTP_201_CREATED: UploadedIconSerializer,
        },
        manual_parameters=[
            openapi.Parameter('file', openapi.IN_FORM, type=openapi.TYPE_FILE, description='Icon file to be uploaded'),
        ],
        operation_id="upload icon"
    )
    def post(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        serializer = UploadedIconSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

