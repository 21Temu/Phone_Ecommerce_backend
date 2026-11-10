from django.contrib import admin
from .models import Brand, Phone, PhoneImage, PhoneVariant


class PhoneImageInline(admin.TabularInline):
    model = PhoneImage
    extra = 1


class PhoneVariantInline(admin.TabularInline):
    model = PhoneVariant
    extra = 1
    fields = ("color", "storage_gb", "ram_gb", "price", "stock", "sku")


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Phone)
class PhoneAdmin(admin.ModelAdmin):
    list_display = ("__str__", "brand", "condition", "is_active", "created_at")
    list_filter = ("condition", "is_active", "brand")
    search_fields = ("name", "brand__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PhoneImageInline, PhoneVariantInline]


@admin.register(PhoneVariant)
class PhoneVariantAdmin(admin.ModelAdmin):
    list_display = ("__str__", "price", "stock", "sku")
    list_filter = ("phone__brand",)
    search_fields = ("sku", "phone__name", "color")