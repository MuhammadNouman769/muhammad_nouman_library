from django import forms

from apps.books.models import Author, Book
from apps.categories.models import Category
from apps.orders.models import Coupon
from apps.orders.models import Order

TEXT = 'form-control'
SELECT = 'form-select'


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'author', 'category', 'description', 'short_description',
            'language', 'pages', 'isbn', 'published_date',
            'price', 'discount_price', 'cover', 'pdf_file', 'audio_file', 'preview_pages',
            'is_featured', 'is_free', 'is_published', 'is_bestseller',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': TEXT}),
            'author': forms.Select(attrs={'class': SELECT}),
            'category': forms.Select(attrs={'class': SELECT}),
            'description': forms.Textarea(attrs={'class': TEXT, 'rows': 5}),
            'short_description': forms.TextInput(attrs={'class': TEXT}),
            'language': forms.Select(attrs={'class': SELECT}),
            'pages': forms.NumberInput(attrs={'class': TEXT}),
            'isbn': forms.TextInput(attrs={'class': TEXT}),
            'published_date': forms.DateInput(attrs={'class': TEXT, 'type': 'date'}),
            'price': forms.NumberInput(attrs={'class': TEXT}),
            'discount_price': forms.NumberInput(attrs={'class': TEXT}),
            'preview_pages': forms.NumberInput(attrs={'class': TEXT}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'icon', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': TEXT}),
            'description': forms.Textarea(attrs={'class': TEXT, 'rows': 3}),
            'icon': forms.TextInput(attrs={'class': TEXT, 'placeholder': 'bi-book'}),
        }


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio', 'photo']
        widgets = {
            'name': forms.TextInput(attrs={'class': TEXT}),
            'bio': forms.Textarea(attrs={'class': TEXT, 'rows': 3}),
        }


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = ['code', 'discount_percent', 'valid_from', 'valid_to', 'active', 'usage_limit']
        widgets = {
            'code': forms.TextInput(attrs={'class': TEXT}),
            'discount_percent': forms.NumberInput(attrs={'class': TEXT}),
            'valid_from': forms.DateInput(attrs={'class': TEXT, 'type': 'date'}),
            'valid_to': forms.DateInput(attrs={'class': TEXT, 'type': 'date'}),
            'usage_limit': forms.NumberInput(attrs={'class': TEXT}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {'status': forms.Select(attrs={'class': SELECT})}
