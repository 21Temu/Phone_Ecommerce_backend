from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User
from apps.accounts.serializers import UserSerializer
from apps.catalog.models import PhoneVariant
from apps.common.permissions import IsAdminRole
from .models import Order, PaymentProof
from .serializers import OrderSerializer, PaymentProofSerializer


class AdminDashboardView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        today = timezone.now().date()
        total_orders = Order.objects.count()
        pending_payment = Order.objects.filter(status="pending_payment").count()
        payment_review = Order.objects.filter(status="payment_review").count()
        confirmed = Order.objects.filter(status__in=["confirmed", "shipped", "delivered"]).count()
        revenue = (
            Order.objects.filter(status__in=["confirmed", "shipped", "delivered"])
            .aggregate(total=Sum("total"))["total"] or 0
        )
        today_orders = Order.objects.filter(created_at__date=today).count()
        low_stock = list(
            PhoneVariant.objects.filter(stock__lte=5)
            .select_related("phone")
            .values("id", "sku", "stock", "phone__name")[:10]
        )
        return Response({
            "total_orders": total_orders,
            "today_orders": today_orders,
            "pending_payment": pending_payment,
            "payment_review": payment_review,
            "confirmed_orders": confirmed,
            "revenue": float(revenue),
            "low_stock": low_stock,
        })


class AdminOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().prefetch_related("items", "payments").order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAdminRole]
    http_method_names = ["get", "patch", "head", "options"]
    filterset_fields = ["status"]
    search_fields = ["order_number", "customer_name", "customer_email", "customer_phone"]

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        new_status = request.data.get("status")
        allowed = [s[0] for s in Order.STATUS]
        if new_status not in allowed:
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        order.status = new_status
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order, context={"request": request}).data)

    @action(detail=True, methods=["post"], url_path="verify-payment")
    def verify_payment(self, request, pk=None):
        order = self.get_object()
        proof_id = request.data.get("proof_id")
        try:
            proof = order.payments.get(id=proof_id)
        except PaymentProof.DoesNotExist:
            return Response({"detail": "Payment proof not found."}, status=status.HTTP_404_NOT_FOUND)

        proof.is_verified = True
        proof.verified_by = request.user
        proof.verified_at = timezone.now()
        proof.save(update_fields=["is_verified", "verified_by", "verified_at"])

        order.status = "confirmed"
        order.save(update_fields=["status"])
        return Response(OrderSerializer(order, context={"request": request}).data)


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [IsAdminRole]
    search_fields = ["username", "email", "phone"]

    @action(detail=True, methods=["post"], url_path="block")
    def block(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser:
            return Response({"detail": "Cannot block superuser."}, status=status.HTTP_400_BAD_REQUEST)
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response({"id": user.id, "is_active": user.is_active})