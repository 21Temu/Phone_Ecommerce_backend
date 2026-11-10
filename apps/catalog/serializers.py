from rest_framework import serializers
from .models import Brand, Phone, PhoneImage, PhoneVariant


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug")


class PhoneImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = PhoneImage
        fields = ("id", "image", "is_primary", "order")

    def get_image(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class PhoneVariantSerializer(serializers.ModelSerializer):
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = PhoneVariant
        fields = (
            "id", "color", "storage_gb", "ram_gb",
            "price", "stock", "in_stock", "sku",
        )


class PhoneListSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    min_price = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Phone
        fields = (
            "id", "slug", "name", "brand", "condition",
            "min_price", "in_stock", "primary_image",
            "screen_size", "battery_mah", "camera_mp", "os",
        )

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if not img:
            return None
        request = self.context.get("request")
        return request.build_absolute_uri(img.image.url) if request else img.image.url


class PhoneDetailSerializer(serializers.ModelSerializer):
    brand = BrandSerializer(read_only=True)
    images = PhoneImageSerializer(many=True, read_only=True)
    variants = PhoneVariantSerializer(many=True, read_only=True)
    in_stock = serializers.ReadOnlyField()

    class Meta:
        model = Phone
        fields = (
            "id", "slug", "name", "brand", "description", "condition",
            "screen_size", "battery_mah", "camera_mp", "os",
            "images", "variants", "in_stock",
            "created_at", "updated_at",
        )