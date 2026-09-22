from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.books.models import Author, Book, Review
from apps.categories.models import Category
from apps.orders.models import Coupon, Order

from .forms import AuthorForm, BookForm, CategoryForm, CouponForm, OrderStatusForm


def staff_required(view_func):
    """Custom-dashboard access control — no reliance on Django's admin app."""
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "You don't have access to the dashboard.")
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return _wrapped


# ---------------------------------------------------------------- overview
@staff_required
def overview(request):
    context = {
        'total_books': Book.objects.count(),
        'total_orders': Order.objects.count(),
        'total_customers': User.objects.filter(is_staff=False).count(),
        'total_revenue': Order.objects.filter(status='completed').aggregate(s=Sum('grand_total'))['s'] or 0,
        'recent_orders': Order.objects.select_related('user').order_by('-created_at')[:8],
        'popular_books': Book.objects.order_by('-views_count')[:6],
        'low_stock_note': Book.objects.filter(is_published=False).count(),
    }
    return render(request, 'dashboard/overview.html', context)


# ---------------------------------------------------------------- books
@staff_required
def book_list(request):
    books_qs = Book.objects.select_related('author', 'category').order_by('-created_at')
    q = request.GET.get('q', '').strip()
    if q:
        books_qs = books_qs.filter(title__icontains=q)
    paginator = Paginator(books_qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/book_list.html', {'page_obj': page, 'books': page.object_list, 'q': q})


@staff_required
def book_add(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book added successfully.')
            return redirect('dashboard:book_list')
    else:
        form = BookForm()
    return render(request, 'dashboard/book_form.html', {'form': form, 'title': 'Add Book'})


@staff_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully.')
            return redirect('dashboard:book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'dashboard/book_form.html', {'form': form, 'title': f'Edit — {book.title}', 'book': book})


@staff_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        messages.success(request, 'Book deleted.')
        return redirect('dashboard:book_list')
    return redirect('dashboard:book_list')


# ---------------------------------------------------------------- categories
@staff_required
def category_list(request):
    categories = Category.objects.annotate(n_books=Count('books')).order_by('name')
    form = CategoryForm()
    return render(request, 'dashboard/category_list.html', {'categories': categories, 'form': form})


@staff_required
def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
    return redirect('dashboard:category_list')


@staff_required
def category_delete(request, pk):
    get_object_or_404(Category, pk=pk).delete()
    messages.success(request, 'Category deleted.')
    return redirect('dashboard:category_list')


# ---------------------------------------------------------------- authors
@staff_required
def author_list(request):
    authors = Author.objects.annotate(n_books=Count('books')).order_by('name')
    form = AuthorForm()
    return render(request, 'dashboard/author_list.html', {'authors': authors, 'form': form})


@staff_required
def author_add(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author added.')
    return redirect('dashboard:author_list')


# ---------------------------------------------------------------- orders
@staff_required
def order_list(request):
    orders_qs = Order.objects.select_related('user').order_by('-created_at')
    status = request.GET.get('status', '')
    if status:
        orders_qs = orders_qs.filter(status=status)
    paginator = Paginator(orders_qs, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/order_list.html', {'page_obj': page, 'orders': page.object_list, 'status': status})


@staff_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Order status updated.')
            return redirect('dashboard:order_detail', pk=pk)
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'dashboard/order_detail.html', {'order': order, 'form': form})


# ---------------------------------------------------------------- customers
@staff_required
def customer_list(request):
    customers = User.objects.filter(is_staff=False).annotate(n_orders=Count('orders')).order_by('-date_joined')
    paginator = Paginator(customers, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/customer_list.html', {'page_obj': page, 'customers': page.object_list})


# ---------------------------------------------------------------- audio books
@staff_required
def audiobook_list(request):
    books = Book.objects.exclude(audio_file='').select_related('author')
    return render(request, 'dashboard/audiobook_list.html', {'books': books})


# ---------------------------------------------------------------- downloads
@staff_required
def download_list(request):
    books = Book.objects.order_by('-downloads_count')[:50]
    return render(request, 'dashboard/download_list.html', {'books': books})


# ---------------------------------------------------------------- reviews
@staff_required
def review_list(request):
    reviews = Review.objects.select_related('user', 'book').order_by('-created_at')
    paginator = Paginator(reviews, 20)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/review_list.html', {'page_obj': page, 'reviews': page.object_list})


@staff_required
def review_toggle(request, pk):
    review = get_object_or_404(Review, pk=pk)
    review.is_approved = not review.is_approved
    review.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'ok', 'is_approved': review.is_approved})
    return redirect('dashboard:review_list')


# ---------------------------------------------------------------- coupons
@staff_required
def coupon_list(request):
    coupons = Coupon.objects.order_by('-valid_to')
    form = CouponForm()
    return render(request, 'dashboard/coupon_list.html', {'coupons': coupons, 'form': form})


@staff_required
def coupon_add(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created.')
    return redirect('dashboard:coupon_list')


# ---------------------------------------------------------------- reports
@staff_required
def reports(request):
    context = {
        'top_books': Book.objects.order_by('-views_count')[:10],
        'top_selling': Book.objects.annotate(n=Count('order_items')).order_by('-n')[:10],
        'orders_by_status': Order.objects.values('status').annotate(n=Count('id')),
        'revenue_total': Order.objects.filter(status='completed').aggregate(s=Sum('grand_total'))['s'] or 0,
    }
    return render(request, 'dashboard/reports.html', context)


# ---------------------------------------------------------------- settings / profile
@staff_required
def website_settings(request):
    return render(request, 'dashboard/settings.html')


@staff_required
def dashboard_profile(request):
    return render(request, 'dashboard/profile.html')
