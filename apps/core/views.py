from django.shortcuts import render

from apps.books.models import Book
from apps.categories.models import Category


def home(request):
    featured = Book.objects.filter(is_published=True, is_featured=True)[:8]
    latest = Book.objects.filter(is_published=True).order_by('-created_at')[:8]
    popular = Book.objects.filter(is_published=True).order_by('-views_count')[:8]
    free = Book.objects.filter(is_published=True, is_free=True)[:8]
    categories = Category.objects.filter(is_active=True)[:10]

    context = {
        'featured_books': featured,
        'latest_books': latest,
        'popular_books': popular,
        'free_books': free,
        'categories': categories,
        'total_books': Book.objects.filter(is_published=True).count(),
    }
    return render(request, 'home/index.html', context)


def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    return render(request, 'errors/500.html', status=500)
