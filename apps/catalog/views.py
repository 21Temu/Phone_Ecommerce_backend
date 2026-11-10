import cohere
import numpy as np
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PhoneImage

import json
import re
import traceback
from groq import Groq
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Phone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter

from .filters import PhoneFilter
from .models import Brand, Phone
from .serializers import BrandSerializer, PhoneDetailSerializer, PhoneListSerializer


class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = None


class PhoneListView(generics.ListAPIView):
    queryset = Phone.objects.filter(is_active=True).select_related("brand").prefetch_related("images", "variants")
    serializer_class = PhoneListSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PhoneFilter
    search_fields = ["name", "brand__name"]
    ordering_fields = ["created_at", "name"]
    ordering = ["-created_at"]


class PhoneDetailView(generics.RetrieveAPIView):
    queryset = Phone.objects.filter(is_active=True).select_related("brand").prefetch_related("images", "variants")
    serializer_class = PhoneDetailSerializer
    lookup_field = "slug"


class AIShoppingAssistantView(APIView):
    def post(self, request):
        try:
            user_message = request.data.get("message", "")
            if not user_message:
                return Response({"error": "Message is required"}, status=400)

            client = Groq(api_key=settings.GROQ_API_KEY)
            
            extraction_prompt = """
            You are a helpful assistant for a phone store. 
            Extract search parameters from the user's message. Return ONLY a valid JSON object with these exact keys:
            - "max_price": (number or null)
            - "condition": ("new", "used", "refurbished", or null)
            - "keyword": (e.g. "photography", "gaming", "battery", or null)
            
            User message: "{message}"
            """
            
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": extraction_prompt.format(message=user_message)}],
                model="openai/gpt-oss-120b",
                response_format={"type": "json_object"},
            )
            raw_content = chat_completion.choices[0].message.content
            
            raw_content = re.sub(r'^```json\s*', '', raw_content)
            raw_content = re.sub(r'\s*```$', '', raw_content)
            
            filters = json.loads(raw_content)

            phones = Phone.objects.filter(is_active=True)
            
            if filters.get("max_price"):
                phones = phones.filter(variants__price__lte=filters["max_price"]).distinct()
            if filters.get("condition"):
                phones = phones.filter(condition=filters["condition"])
            if filters.get("keyword"):
                kw = filters["keyword"].lower()
                if kw in ["photography", "camera"]:
                    phones = phones.order_by("-camera_mp")
                else:
                    phones = phones.filter(name__icontains=kw) | phones.filter(description__icontains=kw)

            top_phones = phones[:5]

            if not top_phones:
                return Response({
                    "reply": "I couldn't find any phones matching that request in our store. Try adjusting your budget or keywords!"
                })

            phone_data = []
            for p in top_phones:
                min_variant = p.variants.order_by("price").first()
                phone_data.append({
                    "name": f"{p.brand.name} {p.name}",
                    "price": str(min_variant.price) if min_variant else "N/A",
                    "condition": p.condition,
                    "camera": p.camera_mp,
                    "battery": p.battery_mah,
                    "slug": p.slug
                })

            final_prompt = f"""
            You are a helpful, friendly phone store assistant. 
            The user asked: "{user_message}"
            
            Here are the phones we have in stock that match their needs:
            {json.dumps(phone_data, indent=2)}
            
            Write a short, conversational response recommending the best phone(s) from the list. 
            Mention the price in Ethiopian Birr (ETB) and why it fits their need (e.g., camera quality). 
            Do not make up any phones outside of this list.
            """
            
            final_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": final_prompt}],
                model="openai/gpt-oss-120b",
            )
            ai_reply = final_completion.choices[0].message.content

            return Response({
                "reply": ai_reply,
                "products": phone_data
            })

        except Exception as e:
            # THIS WILL PRINT THE EXACT ERROR TO YOUR TERMINAL
            print("\n" + "="*50)
            print("AI ASSISTANT CRASHED!")
            print(traceback.format_exc())
            print("="*50 + "\n")
            return Response({"error": str(e)}, status=500)

class AIImageSearchView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"error": "No image provided"}, status=400)

        try:
            # 1. Initialize Cohere
            co = cohere.Client(api_key=settings.COHERE_API_KEY)
            
            # 2. Get the vector for the uploaded image
            response = co.embed(
                images=[file_obj.read()],
                model="embed-v4.0",
                input_type="image"
            )
            query_vector = response.embeddings[0]

            # 3. Find the closest images in Postgres using Cosine Distance (pgvector)
            # 'embedding__cosine_distance' is provided by pgvector
            similar_images = PhoneImage.objects.filter(
                embedding__isnull=False
            ).order_by(models.F("embedding").cosine_distance(query_vector))[:4]

            # 4. Return the associated phones
            results = []
            seen_phone_ids = set()
            for img in similar_images:
                if img.phone.id not in seen_phone_ids:
                    seen_phone_ids.add(img.phone.id)
                    results.append({
                        "id": img.phone.id,
                        "slug": img.phone.slug,
                        "name": f"{img.phone.brand.name} {img.phone.name}",
                        "image": img.image.url if img.image else None,
                    })

            return Response({"results": results})

        except Exception as e:
            return Response({"error": str(e)}, status=500)