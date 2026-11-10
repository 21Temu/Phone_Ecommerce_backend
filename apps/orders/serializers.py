from rest_framework import serializers

from apps.catalog.models import PhoneVariant
from .models import Order, OrderItem, PaymentProof


class OrderItemInputSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "product_name", "variant_label", "unit_price", "quantity", "line_total")


class PaymentProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentProof
        fields = ("id", "transaction_ref", "screenshot", "note", "is_verified", "created_at")
        read_only_fields = ("is_verified", "created_at")


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    payments = PaymentProofSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id", "order_number", "status",
            "customer_name", "customer_email", "customer_phone",
            "shipping_address", "note",
            "subtotal", "shipping_fee", "total",
            "items", "payments", "created_at",
        )


class OrderCreateSerializer(serializers.Serializer):
    customer_name = serializers.CharField(max_length=100)
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20)
    shipping_address = serializers.CharField()
    note = serializers.CharField(required=False, allow_blank=True)
    items = OrderItemInputSerializer(many=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Cart is empty.")
        return items

    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data.pop("items")

        variant_ids = [i["variant_id"] for i in items_data]
        variants = {v.id: v for v in PhoneVariant.objects.select_related("phone").filter(id__in=variant_ids)}

        missing = [vid for vid in variant_ids if vid not in variants]
        if missing:
            raise serializers.ValidationError(f"Invalid variant ids: {missing}")

        for i in items_data:
            v = variants[i["variant_id"]]
            if v.stock < i["quantity"]:
                raise serializers.ValidationError(
                    f"Not enough stock for {v}. Only {v.stock} left."
                )

        subtotal = sum(variants[i["variant_id"]].price * i["quantity"] for i in items_data)
        shipping_fee = 0  # change later if you want flat shipping fee
        total = subtotal + shipping_fee

        user = request.user if request.user.is_authenticated else None

        order = Order.objects.create(
            user=user,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            total=total,
            **validated_data,
        )

        for i in items_data:
            v = variants[i["variant_id"]]
            line_total = v.price * i["quantity"]
            OrderItem.objects.create(
                order=order,
                variant=v,
                product_name=f"{v.phone.brand.name} {v.phone.name}",
                variant_label=str(v),
                unit_price=v.price,
                quantity=i["quantity"],
                line_total=line_total,
            )
            v.stock -= i["quantity"]
            v.save(update_fields=["stock"])

        return order