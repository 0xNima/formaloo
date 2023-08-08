from django.contrib.auth.models import User
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from apps.authenticate.serializers import RegisterUserSerializer, LoginUserSerializer, LogoutSerializer
from appstore.utils import CustomSchemes


class RegisterUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterUserSerializer

    @swagger_auto_schema(
        operation_description='Signup new user',
        responses={
            status.HTTP_201_CREATED: CustomSchemes.user
        },
        operation_id="register"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginUserView(TokenObtainPairView):
    permission_classes = (AllowAny,)
    serializer_class = LoginUserSerializer

    @swagger_auto_schema(
        operation_description='Login',
        responses={
            status.HTTP_200_OK: CustomSchemes.token_pair,
        },
        operation_id="login"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):
    @swagger_auto_schema(
        operation_description='Refresh access token',
        responses={
            status.HTTP_200_OK: CustomSchemes.token_pair,
            status.HTTP_400_BAD_REQUEST: CustomSchemes.error,
            status.HTTP_401_UNAUTHORIZED: CustomSchemes.error
        },
        operation_id="refresh token"
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LogoutUserView(GenericAPIView):
    serializer_class = LogoutSerializer

    @swagger_auto_schema(
        operation_description='Logout',
        responses={
            status.HTTP_204_NO_CONTENT: '',
            status.HTTP_400_BAD_REQUEST: CustomSchemes.error,
            status.HTTP_401_UNAUTHORIZED: CustomSchemes.error
        },
        operation_id="logout"
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
