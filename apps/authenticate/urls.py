from django.urls import path
from apps.authenticate.views import RegisterUserView, LoginUserView, RefreshTokenView, LogoutUserView


urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='auth_register'),
    path('login/', LoginUserView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
]
