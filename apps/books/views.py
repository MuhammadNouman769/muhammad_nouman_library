from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from .forms import ReviewForm
from .models import Author, Book, Review, Wishlist

PAGE_SIZE = 12


def _paginate(request, qs, page_size=PAGE_SIZE):
    paginator = Paginator(qs, page_size)
    return paginator.get_page(request.GET.get('page'))


def book_list(request):
    """All Books page with AJAX search + advanced filters (no reload)."""
    books_qs = Book.objects.filter(is_published=True).select_related('author', 'category')

    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '')
    language = request.GET.get('language', '')
    price = request.GET.get('price', '')  # free | paid
    sort = request.GET.get('sort', 'latest')

    if q:
        books_qs = books_qs.filter(
            Q(title__icontains=q) | Q(author__name__icontains=q) | Q(description__icontains=q)
        )
    if category:
        books_qs = books_qs.filter(category__slug=category)
    if language:
        books_qs = books_qs.filter(language=language)
    if price == 'free':
        books_qs = books_qs.filter(is_free=True)
    elif price == 'paid':
        books_qs = books_qs.filter(is_free=False)

    sort_map = {
        'latest': '-created_at',
        'popular': '-views_count',
        'price_low': 'price',
        'price_high': '-price',
        'title': 'title',
    }
    books_qs = books_qs.order_by(sort_map.get(sort, '-created_at'))

    page = _paginate(request, books_qs)
    context = {'page_obj': page, 'books': page.object_list, 'q': q}

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('books/_book_grid.html', context, request=request)
        return JsonResponse({'html': html, 'count': books_qs.count()})

    return render(request, 'books/book_list.html', context)


def book_detail(request, slug):
    book = get_object_or_404(Book.objects.select_related('author', 'category'), slug=slug, is_published=True)
    Book.objects.filter(pk=book.pk).update(views_count=book.views_count + 1)

    related_books = Book.objects.filter(category=book.category, is_published=True).exclude(pk=book.pk)[:6]
    reviews = book.reviews.filter(is_approved=True).select_related('user')
    review_form = ReviewForm()

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, book=book).exists()

    context = {
        'book': book,
        'related_books': related_books,
        'reviews': reviews,
        'review_form': review_form,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'books/book_detail.html', context)


def book_preview(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    return render(request, 'books/book_preview.html', {'book': book})


def featured_books(request):
    books_qs = Book.objects.filter(is_published=True, is_featured=True)
    page = _paginate(request, books_qs)
    return render(request, 'books/book_list.html', {
        'page_obj': page, 'books': page.object_list, 'page_title': 'Featured Books'
    })


def latest_books(request):
    books_qs = Book.objects.filter(is_published=True).order_by('-created_at')
    page = _paginate(request, books_qs)
    return render(request, 'books/book_list.html', {
        'page_obj': page, 'books': page.object_list, 'page_title': 'Latest Books'
    })


def popular_books(request):
    books_qs = Book.objects.filter(is_published=True).order_by('-views_count')
    page = _paginate(request, books_qs)
    return render(request, 'books/book_list.html', {
        'page_obj': page, 'books': page.object_list, 'page_title': 'Popular Books'
    })


def free_books(request):
    books_qs = Book.objects.filter(is_published=True, is_free=True)
    page = _paginate(request, books_qs)
    return render(request, 'books/book_list.html', {
        'page_obj': page, 'books': page.object_list, 'page_title': 'Free Books'
    })


def author_list(request):
    authors = Author.objects.all()
    return render(request, 'books/authors.html', {'authors': authors})


def author_detail(request, slug):
    author = get_object_or_404(Author, slug=slug)
    books_qs = Book.objects.filter(author=author, is_published=True)
    page = _paginate(request, books_qs)
    return render(request, 'books/author_detail.html', {
        'author': author, 'page_obj': page, 'books': page.object_list
    })


# ---------- AJAX endpoints ----------

@login_required
@require_POST
def toggle_wishlist(request, slug):
    book = get_object_or_404(Book, slug=slug)
    wish, created = Wishlist.objects.get_or_create(user=request.user, book=book)
    if not created:
        wish.delete()
        return JsonResponse({'status': 'removed', 'in_wishlist': False})
    return JsonResponse({'status': 'added', 'in_wishlist': True})


@login_required
@require_POST
def submit_review(request, slug):
    book = get_object_or_404(Book, slug=slug)
    form = ReviewForm(request.POST)
    if form.is_valid():
        review, _ = Review.objects.update_or_create(
            book=book, user=request.user,
            defaults={'rating': form.cleaned_data['rating'], 'comment': form.cleaned_data['comment']}
        )
        html = render_to_string('books/_review_item.html', {'review': review}, request=request)
        return JsonResponse({
            'status': 'ok', 'html': html,
            'average_rating': book.average_rating, 'review_count': book.review_count,
        })
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


def live_search(request):
    """Navbar live search-as-you-type suggestion box."""
    q = request.GET.get('q', '').strip()
    results = []
    if len(q) >= 2:
        books_qs = Book.objects.filter(is_published=True, title__icontains=q).select_related('author')[:8]
        results = [{
            'title': b.title,
            'author': b.author.name,
            'url': b.get_absolute_url(),
            'cover': b.cover.url if b.cover else '',
            'price': str(b.final_price),
            'is_free': b.is_free,
        } for b in books_qs]
    return JsonResponse({'results': results})
