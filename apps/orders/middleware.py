from .cart import Cart


class CartMiddleware:
    """Attaches request.cart so every view/template can access the session cart."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.cart = Cart(request)
        return self.get_response(request)
