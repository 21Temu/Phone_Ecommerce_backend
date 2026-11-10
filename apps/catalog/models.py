from django.db import models
from django.utils.text import slugify
from apps.common.models import TimeStampedModel


class Brand(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Phone(TimeStampedModel):
    CONDITION_CHOICES = (
        ("new", "New"),
        ("used", "Used"),
        ("refurbished", "Refurbished"),
    )

    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="phones")
    name = models.CharField(max_length=200)              # "iPhone 15 Pro"
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    is_active = models.BooleanField(default=True)

    # Spec sheet — used for filters now, and for AI later
    screen_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    battery_mah = models.PositiveIntegerField(null=True, blank=True)
    camera_mp = models.PositiveIntegerField(null=True, blank=True)
    os = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["condition", "is_active"]),
            models.Index(fields=["brand"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.brand.name}-{self.name}")
            slug = base
            i = 1
            while Phone.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    @property
    def min_price(self):
        prices = [v.price for v in self.variants.all() if v.stock > 0]
        return min(prices) if prices else None

    @property
    def in_stock(self):
        return self.variants.filter(stock__gt=0).exists()


class PhoneImage(TimeStampedModel):
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="phones/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-is_primary", "order"]


class PhoneVariant(TimeStampedModel):
    phone = models.ForeignKey(Phone, on_delete=models.CASCADE, related_name="variants")
    color = models.CharField(max_length=50)
    storage_gb = models.PositiveIntegerField()
    ram_gb = models.PositiveIntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=64, unique=True)

    class Meta:
        ordering = ["phone", "storage_gb", "color"]
        constraints = [
            models.UniqueConstraint(
                fields=["phone", "color", "storage_gb", "ram_gb"],
                name="uniq_variant_per_phone",
            )
        ]

    def __str__(self):
        parts = [self.phone.name, self.color, f"{self.storage_gb}GB"]
        if self.ram_gb:
            parts.append(f"{self.ram_gb}GB RAM")
        return " · ".join(parts)

    @property
    def in_stock(self):
        return self.stock > 0