def cart_summary(request):
    cart = getattr(request, 'cart', None)
    if cart is None:
        return {'cart_count': 0, 'cart_total': 0}
    return {'cart_count': len(cart), 'cart_total': cart.get_total_price()}
