from django.urls import path
from rest_framework.routers import DefaultRouter
from apps.core.views import AppViewsets, VerifiedAppsView, PurchaseViewsets


router = DefaultRouter()
router.register(r'apps', AppViewsets, basename='apps')
router.register(r'purchases', PurchaseViewsets, basename='purchases')

urlpatterns = [
    path('apps/verified/', VerifiedAppsView.as_view()),
    # path('apps/purchases/', PurchasedAppsView.as_view()),
    # path('apps/purchases/<int:pk>', PurchasedAppDetailView.as_view()),
] + router.urls
