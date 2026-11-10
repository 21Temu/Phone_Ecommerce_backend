import requests
import uuid

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order

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

class InitiateChapaPaymentView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # 1. Make tx_ref unique so Chapa doesn't reject it
        tx_ref = f"{order.order_number}-{uuid.uuid4().hex[:6]}"
        
        # 2. Ensure the amount is a valid float string (e.g., "1000.00")
        amount = f"{order.total:.2f}"
        
        # 3. Use a generic placeholder for testing if needed. 
        # Chapa test mode usually accepts localhost, but if it fails, use a real domain.
        frontend_url = "http://localhost:5173"
        callback_url = f"{frontend_url}/track?success=1&order={order.order_number}"

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "amount": amount,
            "currency": "ETB",
            "email": order.customer_email or "customer@example.com", # Fallback if email is missing
            "first_name": order.customer_name.split()[0] if order.customer_name else "Customer",
            "last_name": order.customer_name.split()[-1] if len(order.customer_name.split()) > 1 else "User",
            "phone_number": order.customer_phone or "0900000000", # Fallback
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": callback_url,
            "customization": {
                "title": "PhoneStore Payment",
                "description": f"Payment for order {order.order_number}"
            }
        }

        # Call Chapa API
        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            json=payload,
            headers=headers,
        )

        if response.status_code == 200:
            data = response.json()
            checkout_url = data.get("data", {}).get("checkout_url")
            if checkout_url:
                return Response({"checkout_url": checkout_url})
            return Response({"detail": "No checkout URL returned."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # THIS IS THE KEY PART: Print the exact error from Chapa to your terminal
            print("CHAPA ERROR RESPONSE:", response.text)
            
            try:
                error_msg = response.json().get("message", "Chapa initialization failed.")
            except:
                error_msg = response.text
                
            return Response(
                {"detail": f"Chapa Error: {error_msg}"},
                status=status.HTTP_400_BAD_REQUEST,
            )