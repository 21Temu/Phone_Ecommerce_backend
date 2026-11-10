from rest_framework import serializers
from .models import Brand, Phone, PhoneImage, PhoneVariant


class BrandAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")
        read_only_fields = ("slug",)


class PhoneVariantAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneVariant
        fields = (
            "id", "phone", "color", "storage_gb", "ram_gb",
            "price", "stock", "sku",
        )


class PhoneImageAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneImage
        fields = ("id", "phone", "image", "is_primary", "order")


class PhoneAdminSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)
    variants = PhoneVariantAdminSerializer(many=True, read_only=True)
    images = PhoneImageAdminSerializer(many=True, read_only=True)

    class Meta:
        model = Phone
        fields = (
            "id", "slug", "name", "brand", "brand_name",
            "description", "condition",
            "screen_size", "battery_mah", "camera_mp", "os",
            "is_active", "variants", "images",
            "created_at", "updated_at",
        )
        read_only_fields = ("slug", "created_at", "updated_at")