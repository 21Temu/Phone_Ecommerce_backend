import uuid

from django.conf import settings
from django.db import models

from apps.catalog.models import PhoneVariant
from apps.common.models import TimeStampedModel


def generate_order_number():
    return f"ORD-{uuid.uuid4().hex[:10].upper()}"


class Order(TimeStampedModel):
    STATUS = (
        ("pending_payment", "Pending Payment"),
        ("payment_review", "Payment Under Review"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=(("offline", "Offline Transfer"), ("chapa", "Chapa Online")),
        default="offline",
    )

    order_number = models.CharField(max_length=20, unique=True, default=generate_order_number)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="orders",
    )
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    shipping_address = models.TextField()
    note = models.TextField(blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default="pending_payment")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.order_number


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(PhoneVariant, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=200)
    variant_label = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=12, decimal_places=2)


class PaymentProof(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    transaction_ref = models.CharField(max_length=100)
    screenshot = models.ImageField(upload_to="payments/")
    note = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    verified_at = models.DateTimeField(null=True, blank=True)