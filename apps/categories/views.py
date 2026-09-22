from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from apps.books.models import Book
from .models import Category


def category_list(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'books/categories.html', {'categories': categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    books_qs = Book.objects.filter(category=category, is_published=True)
    paginator = Paginator(books_qs, 12)
    page = paginator.get_page(request.GET.get('page'))
    context = {'category': category, 'page_obj': page, 'books': page.object_list}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'books/_book_grid.html', context)
    return render(request, 'books/category_detail.html', context)
