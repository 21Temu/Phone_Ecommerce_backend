from django.urls import path
from .views import InitiateChapaPaymentView

from .views import (
    MyOrdersView,
    OrderCreateView,
    OrderTrackView,
    UploadPaymentProofView,
)

urlpatterns = [
    path("", OrderCreateView.as_view(), name="order-create"),
    path("track/", OrderTrackView.as_view(), name="order-track"),
    path("my/", MyOrdersView.as_view(), name="order-my"),
    path("<int:order_id>/pay-proof/", UploadPaymentProofView.as_view(), name="order-pay-proof"),
    path("<int:order_id>/chapa-initiate/", InitiateChapaPaymentView.as_view(), name="order-chapa-initiate"),
]