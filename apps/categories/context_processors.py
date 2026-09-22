from .models import Category


def category_menu(request):
    """Makes the active category list available on every page (navbar/footer)."""
    categories = Category.objects.filter(is_active=True).order_by('name')
    return {'nav_categories': categories}
