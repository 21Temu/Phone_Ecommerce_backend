# config/admin_urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import MeView
from apps.catalog.admin_views import (
    AdminBrandViewSet,
    AdminPhoneImageViewSet,
    AdminPhoneViewSet,
    AdminVariantViewSet,
)
from apps.orders.admin_views import AdminDashboardView, AdminOrderViewSet, AdminUserViewSet

router = DefaultRouter()
router.register("brands", AdminBrandViewSet, basename="admin-brands")
router.register("phones", AdminPhoneViewSet, basename="admin-phones")
router.register("variants", AdminVariantViewSet, basename="admin-variants")
router.register("images", AdminPhoneImageViewSet, basename="admin-images")
router.register("orders", AdminOrderViewSet, basename="admin-orders")
router.register("users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("", include(router.urls)),
]