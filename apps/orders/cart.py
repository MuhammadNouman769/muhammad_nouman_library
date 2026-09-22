"""
Session-based shopping cart. Works without login; merges to Order at checkout.
"""
from decimal import Decimal

from django.conf import settings

from apps.books.models import Book


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, book, quantity=1):
        book_id = str(book.id)
        if book_id not in self.cart:
            self.cart[book_id] = {'quantity': 0, 'price': str(book.final_price)}
        self.cart[book_id]['quantity'] += quantity
        self.save()

    def remove(self, book):
        book_id = str(book.id)
        if book_id in self.cart:
            del self.cart[book_id]
            self.save()

    def update(self, book, quantity):
        book_id = str(book.id)
        if book_id in self.cart:
            if quantity <= 0:
                del self.cart[book_id]
            else:
                self.cart[book_id]['quantity'] = quantity
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.save()

    def __iter__(self):
        book_ids = self.cart.keys()
        books = Book.objects.filter(id__in=book_ids)
        cart = self.cart.copy()
        for book in books:
            cart[str(book.id)]['book'] = book
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
