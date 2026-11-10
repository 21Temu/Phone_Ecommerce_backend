from rest_framework import viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from apps.common.permissions import IsAdminRole
from .admin_serializers import (
    BrandAdminSerializer,
    PhoneAdminSerializer,
    PhoneImageAdminSerializer,
    PhoneVariantAdminSerializer,
)
from .models import Brand, Phone, PhoneImage, PhoneVariant


class AdminBrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all().order_by("name")
    serializer_class = BrandAdminSerializer
    permission_classes = [IsAdminRole]


class AdminPhoneViewSet(viewsets.ModelViewSet):
    queryset = Phone.objects.all().select_related("brand").prefetch_related("variants", "images")
    serializer_class = PhoneAdminSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["brand", "condition", "is_active"]
    search_fields = ["name", "brand__name"]


class AdminVariantViewSet(viewsets.ModelViewSet):
    queryset = PhoneVariant.objects.all().select_related("phone")
    serializer_class = PhoneVariantAdminSerializer
    permission_classes = [IsAdminRole]
    filterset_fields = ["phone"]


class AdminPhoneImageViewSet(viewsets.ModelViewSet):
    queryset = PhoneImage.objects.all()
    serializer_class = PhoneImageAdminSerializer
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filterset_fields = ["phone"]