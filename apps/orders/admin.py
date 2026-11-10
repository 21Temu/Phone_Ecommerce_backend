from django.contrib import admin
from .models import Order, OrderItem, PaymentProof


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product_name", "variant_label", "unit_price", "quantity", "line_total")


class PaymentProofInline(admin.TabularInline):
    model = PaymentProof
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer_name", "status", "total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("order_number", "customer_name", "customer_email", "customer_phone")
    inlines = [OrderItemInline, PaymentProofInline]


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("order", "transaction_ref", "is_verified", "created_at")
    list_filter = ("is_verified",)