from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from apps.books.models import Book


def audiobook_list(request):
    """Audio Books page — every book that has an audio_file attached."""
    books_qs = Book.objects.filter(is_published=True).exclude(audio_file='').select_related('author', 'category')
    paginator = Paginator(books_qs, 12)
    page = paginator.get_page(request.GET.get('page'))
    context = {'page_obj': page, 'books': page.object_list}
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'books/_book_grid.html', context)
    return render(request, 'books/audiobooks.html', context)


def player_data(request, slug):
    """AJAX endpoint the player uses to load a track without reloading the page."""
    book = get_object_or_404(Book, slug=slug, is_published=True)
    return JsonResponse({
        'title': book.title,
        'author': book.author.name,
        'audio_url': book.audio_file.url if book.audio_file else '',
        'cover_url': book.cover.url if book.cover else '',
    })
