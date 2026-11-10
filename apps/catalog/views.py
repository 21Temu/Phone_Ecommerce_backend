from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import PhoneFilter
from .models import Brand, Phone
from .serializers import BrandSerializer, PhoneDetailSerializer, PhoneListSerializer


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = None


class PhoneListView(generics.ListAPIView):
    queryset = Phone.objects.filter(is_active=True).select_related("brand").prefetch_related("images", "variants")
    serializer_class = PhoneListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PhoneFilter
    search_fields = ["name", "brand__name"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]


class PhoneDetailView(generics.RetrieveAPIView):
    queryset = Phone.objects.filter(is_active=True).select_related("brand").prefetch_related("images", "variants")
    serializer_class = PhoneDetailSerializer
    lookup_field = "slug"