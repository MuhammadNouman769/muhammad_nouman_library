from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .forms import ContactForm


def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    form = ContactForm()
    return render(request, 'pages/contact.html', {'form': form})


@require_POST
def contact_submit(request):
    """AJAX contact form submit — no page reload."""
    form = ContactForm(request.POST)
    if form.is_valid():
        # In production this would send an email / save a Lead model.
        return JsonResponse({'status': 'ok', 'message': "Thanks! We'll get back to you soon."})
    return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)


def faq(request):
    faqs = [
        ("How do I read a book online?", "Open any book's detail page and click \"Read Online\" — no download needed."),
        ("Can I download books as PDF?", "Yes, most books offer a \"Download PDF\" button on the book detail page."),
        ("Do you have audiobooks?", "Many titles include a \"Listen Audio\" player right on the book page."),
        ("Which languages are supported?", "You can switch the whole site between English, Urdu and Arabic from the navbar."),
        ("Are there free books?", "Yes — check the \"Free Books\" section from the navbar or homepage."),
        ("How do I pay for a paid book?", "Add books to your cart, proceed to checkout, and complete your order. Payment gateways can be added later."),
        ("Can I get a refund?", "See our Refund Policy page for full details on eligibility and process."),
    ]
    return render(request, 'pages/faq.html', {'faqs': faqs})


def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')


def terms_of_use(request):
    return render(request, 'pages/terms_of_use.html')


def refund_policy(request):
    return render(request, 'pages/refund_policy.html')


def shipping_policy(request):
    return render(request, 'pages/shipping_policy.html')


def copyright_page(request):
    return render(request, 'pages/copyright.html')
