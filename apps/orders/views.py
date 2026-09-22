from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils import timezone
from django.views.decorators.http import require_POST

from apps.books.models import Book

from .forms import CheckoutForm
from .models import Coupon, Order, OrderItem


def cart_detail(request):
    return render(request, 'orders/cart.html', {'cart': request.cart})


@require_POST
def cart_add(request, book_id):
    book = get_object_or_404(Book, id=book_id, is_published=True)
    quantity = int(request.POST.get('quantity', 1))
    request.cart.add(book, quantity=quantity)
    html = render_to_string('orders/_cart_mini.html', {'cart': request.cart}, request=request)
    return JsonResponse({'status': 'ok', 'cart_count': len(request.cart), 'mini_cart_html': html})


@require_POST
def cart_remove(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    request.cart.remove(book)
    html = render_to_string('orders/_cart_table.html', {'cart': request.cart}, request=request)
    return JsonResponse({'status': 'ok', 'cart_count': len(request.cart),
                          'cart_total': str(request.cart.get_total_price()), 'table_html': html})


@require_POST
def cart_update(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    quantity = int(request.POST.get('quantity', 1))
    request.cart.update(book, quantity)
    html = render_to_string('orders/_cart_table.html', {'cart': request.cart}, request=request)
    return JsonResponse({'status': 'ok', 'cart_count': len(request.cart),
                          'cart_total': str(request.cart.get_total_price()), 'table_html': html})


@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '').strip()
    try:
        coupon = Coupon.objects.get(code__iexact=code)
        if not coupon.is_valid():
            return JsonResponse({'status': 'error', 'message': 'This coupon has expired or is no longer valid.'})
    except Coupon.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Invalid coupon code.'})

    request.session['coupon_code'] = coupon.code
    subtotal = request.cart.get_total_price()
    discount = subtotal * coupon.discount_percent / 100
    return JsonResponse({
        'status': 'ok', 'discount_percent': coupon.discount_percent,
        'discount_amount': str(discount), 'new_total': str(subtotal - discount),
    })


@login_required
def checkout(request):
    if len(request.cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('books:list')

    coupon = None
    coupon_code = request.session.get('coupon_code')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code).first()

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            subtotal = request.cart.get_total_price()
            discount = (subtotal * coupon.discount_percent / 100) if coupon else 0
            order = form.save(commit=False)
            order.user = request.user
            order.coupon = coupon
            order.subtotal = subtotal
            order.discount_total = discount
            order.grand_total = subtotal - discount
            order.save()

            for item in request.cart:
                OrderItem.objects.create(
                    order=order, book=item['book'], title=item['book'].title,
                    price=item['price'], quantity=item['quantity'],
                )

            if coupon:
                coupon.used_count += 1
                coupon.save()
                del request.session['coupon_code']

            request.cart.clear()
            return redirect('orders:success', order_id=order.id)
    else:
        form = CheckoutForm(initial={
            'full_name': request.user.get_full_name(), 'email': request.user.email,
        })

    discount_percent = coupon.discount_percent if coupon else 0
    return render(request, 'orders/checkout.html', {
        'form': form, 'cart': request.cart, 'coupon': coupon, 'discount_percent': discount_percent,
    })


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
