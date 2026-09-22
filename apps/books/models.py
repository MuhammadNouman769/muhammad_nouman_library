from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.categories.models import Category


class Author(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='authors/', blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:author_detail', args=[self.slug])

    @property
    def book_count(self):
        return self.books.filter(is_published=True).count()


class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ur', 'Urdu'),
        ('ar', 'Arabic'),
    ]

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books')
    description = models.TextField(blank=True)
    short_description = models.CharField(max_length=300, blank=True)

    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    pages = models.PositiveIntegerField(default=0)
    isbn = models.CharField(max_length=20, blank=True)
    published_date = models.DateField(null=True, blank=True)

    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    pdf_file = models.FileField(upload_to='books/', blank=True, null=True)
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    preview_pages = models.PositiveIntegerField(default=10, help_text="Pages visible in free preview")

    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    is_bestseller = models.BooleanField(default=False)

    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_published', 'is_featured']),
            models.Index(fields=['is_published', 'is_free']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Book.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:detail', args=[self.slug])

    @property
    def final_price(self):
        if self.is_free:
            return 0
        if self.discount_price:
            return self.discount_price
        return self.price

    @property
    def has_discount(self):
        return bool(self.discount_price and self.discount_price < self.price)

    @property
    def discount_percent(self):
        if self.has_discount and self.price:
            return round((1 - (self.discount_price / self.price)) * 100)
        return 0

    @property
    def has_audio(self):
        return bool(self.audio_file)

    @property
    def average_rating(self):
        agg = self.reviews.filter(is_approved=True).aggregate(models.Avg('rating'))
        return round(agg['rating__avg'] or 0, 1)

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='book_reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('book', 'user')

    def __str__(self):
        return f"{self.user} → {self.book} ({self.rating}★)"


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user} ♥ {self.book}"
