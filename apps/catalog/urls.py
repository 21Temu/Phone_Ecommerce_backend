from django.urls import path
from .views import BrandListView, PhoneDetailView, PhoneListView
from .views import AIShoppingAssistantView
from .views import AIImageSearchView

urlpatterns = [
    path("brands/", BrandListView.as_view(), name="brand-list"),
    path("phones/", PhoneListView.as_view(), name="phone-list"),
    path("phones/<slug:slug>/", PhoneDetailView.as_view(), name="phone-detail"),
    path("ai-assistant/", AIShoppingAssistantView.as_view(), name="ai-assistant"),
    path("image-search/", AIImageSearchView.as_view(), name="image-search"),
]