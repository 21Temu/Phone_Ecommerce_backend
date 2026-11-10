import django_filters
from .models import Phone


class PhoneFilter(django_filters.FilterSet):
    brand = django_filters.CharFilter(field_name="brand__slug")
    condition = django_filters.CharFilter(field_name="condition")
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_price = django_filters.NumberFilter(method="filter_max_price")
    storage = django_filters.NumberFilter(method="filter_storage")
    ram = django_filters.NumberFilter(method="filter_ram")
    search = django_filters.CharFilter(method="filter_search")

    class Meta:
        model = Phone
        fields = []

    def filter_min_price(self, qs, name, value):
        return qs.filter(variants__price__gte=value).distinct()

    def filter_max_price(self, qs, name, value):
        return qs.filter(variants__price__lte=value).distinct()

    def filter_storage(self, qs, name, value):
        return qs.filter(variants__storage_gb=value).distinct()

    def filter_ram(self, qs, name, value):
        return qs.filter(variants__ram_gb=value).distinct()

    def filter_search(self, qs, name, value):
        return qs.filter(name__icontains=value) | qs.filter(brand__name__icontains=value)