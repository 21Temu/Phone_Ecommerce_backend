from rest_framework import generics, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order, PaymentProof
from .serializers import OrderCreateSerializer, OrderSerializer, PaymentProofSerializer


class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            OrderSerializer(order, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class OrderTrackView(APIView):
    def get(self, request):
        order_number = request.query_params.get("order_number", "").strip()
        email = request.query_params.get("email", "").strip().lower()
        if not order_number or not email:
            return Response(
                {"detail": "order_number and email required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            order = Order.objects.get(order_number=order_number, customer_email__iexact=email)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order, context={"request": request}).data)


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items", "payments")


class UploadPaymentProofView(generics.CreateAPIView):
    serializer_class = PaymentProofSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, order_id, *args, **kwargs):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        proof = serializer.save(order=order)

        order.status = "payment_review"
        order.save(update_fields=["status"])

        return Response(
            PaymentProofSerializer(proof, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )