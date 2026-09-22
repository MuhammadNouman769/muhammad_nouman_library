"""
Seeds the library with realistic dummy data: 12 categories, 40 authors,
and 150 books (with generated placeholder SVG covers, tiny placeholder
PDF and MP3 files so every feature — read/download/listen — has something
to click on). Safe to re-run: uses get_or_create.

Usage:
    python manage.py seed_books
    python manage.py seed_books --count 150
"""
import base64
import random
from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.books.models import Author, Book
from apps.categories.models import Category

CATEGORIES = [
    ("Fiction", "bi-book"),
    ("Non-Fiction", "bi-journal-text"),
    ("Science", "bi-atom"),
    ("Technology", "bi-cpu"),
    ("Business", "bi-briefcase"),
    ("Self Help", "bi-emoji-smile"),
    ("History", "bi-hourglass-split"),
    ("Poetry", "bi-feather"),
    ("Biography", "bi-person-lines-fill"),
    ("Religion & Spirituality", "bi-moon-stars"),
    ("Children", "bi-balloon"),
    ("Islamic Studies", "bi-book-half"),
]

AUTHOR_FIRST = ["Ahmed", "Ali", "Sara", "Ayesha", "John", "Emma", "Bilal", "Hassan",
                "Fatima", "Zainab", "Michael", "Sophia", "Usman", "Hira", "David",
                "Maria", "Omar", "Layla", "James", "Noor"]
AUTHOR_LAST = ["Khan", "Ahmed", "Siddiqui", "Malik", "Smith", "Johnson", "Raza",
               "Farooq", "Iqbal", "Chaudhry", "Brown", "Wilson", "Butt", "Shah",
               "Taylor", "Anderson"]

TITLE_WORDS_A = ["The Silent", "Whispers of", "Shadows over", "Journey to", "Beyond the",
                  "The Last", "Echoes of", "Rise of", "The Hidden", "Chronicles of",
                  "The Art of", "A Guide to", "Understanding", "The Power of",
                  "Secrets of", "The Road to", "Tales from", "The Science of",
                  "Mastering", "The Story of"]
TITLE_WORDS_B = ["Time", "the Mountain", "Tomorrow", "the Stars", "Destiny", "Wisdom",
                  "the Heart", "Change", "the Desert", "Empires", "Focus",
                  "Happiness", "the Mind", "Success", "the Sea", "Freedom",
                  "the City", "Data", "Leadership", "the Soul"]

LANGUAGES = ["en", "en", "en", "ur", "ar"]

SVG_PALETTE = ["1c2b4a", "2b3f6b", "8a4b2c", "355e3b", "6a2c4b", "3b3b6d", "4a1c2b"]


def make_cover_svg(title, color):
    safe_title = title.replace('&', 'and')
    words = safe_title.split()
    line1 = " ".join(words[:3])
    line2 = " ".join(words[3:6])
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' width='400' height='560'>
<rect width='400' height='560' fill='#{color}'/>
<rect x='20' y='20' width='360' height='520' fill='none' stroke='#e0a527' stroke-width='3'/>
<text x='200' y='250' font-size='28' fill='#ffffff' font-family='Georgia, serif' text-anchor='middle'>{line1}</text>
<text x='200' y='290' font-size='28' fill='#ffffff' font-family='Georgia, serif' text-anchor='middle'>{line2}</text>
<text x='200' y='500' font-size='16' fill='#e0a527' font-family='Georgia, serif' text-anchor='middle'>Muhammad Nouman Library</text>
</svg>"""
    return svg.encode("utf-8")


MINI_PDF = base64.b64decode(
    "JVBERi0xLjEKJcKlwrHDqwoKMSAwIG9iagogIDw8IC9UeXBlIC9DYXRhbG9nCiAgICAgL1BhZ2Vz"
    "IDIgMCBSCiAgPj4KZW5kb2JqCgoyIDAgb2JqCiAgPDwgL1R5cGUgL1BhZ2VzCiAgICAgL0tpZHMg"
    "WzMgMCBSXQogICAgIC9Db3VudCAxCiAgICAgL01lZGlhQm94IFswIDAgMzAwIDE0NF0KICA+Pgpl"
    "bmRvYmoKCjMgMCBvYmoKICA8PCAgL1R5cGUgL1BhZ2UKICAgICAgL1BhcmVudCAyIDAgUgogICAg"
    "ICAvUmVzb3VyY2VzCiAgICAgICA8PCAvRm9udCA8PCAvRjEgNCAwIFIgPj4gPj4KICAgICAgL0Nv"
    "bnRlbnRzIDUgMCBSCiAgPj4KZW5kb2JqCgo0IDAgb2JqCiAgPDwgL1R5cGUgL0ZvbnQKICAgICAv"
    "U3VidHlwZSAvVHlwZTEKICAgICAvQmFzZUZvbnQgL1RpbWVzLVJvbWFuCiAgPj4KZW5kb2JqCgo1"
    "IDAgb2JqICAlIHBhZ2UgY29udGVudAogIDw8IC9MZW5ndGggNDQgPj4Kc3RyZWFtCkJUCjcwIDUw"
    "IFRECi9GMSAxMiBUZgooTXVoYW1tYWQgTm91bWFuIExpYnJhcnkpIFRqCkVUCmVuZHN0cmVhbQpl"
    "bmRvYmoKCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAow"
    "MDAwMDAwMDc5IDAwMDAwIG4gCjAwMDAwMDAxNzMgMDAwMDAgbiAKMDAwMDAwMDMwMSAwMDAwMCBu"
    "IAowMDAwMDAwMzgwIDAwMDAwIG4gCnRyYWlsZXIKICA8PCAgL1Jvb3QgMSAwIFIKICAgICAgL1Np"
    "emUgNgogID4+CnN0YXJ0eHJlZgo0OTIKJSVFT0YK"
)

# A ~0.2s silent MP3 frame, repeated, so <audio> has a real playable file.
MINI_MP3 = base64.b64decode(
    "//uQxAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAAEAAABIADAwMDAwMDAwMDAwMDAwMDAwMDA"
    "wMDA6urq6urq6urq6urq6urq6urq6v///////////////////////////8AAAAATGF2YzU4LjEz"
    "AAAAAAAAAAAAAAAAJAAAAAAAAAAAASDs90hvAAAAAAAAAAAAAAAAAAAA//OExAADkAWO0AAgAQtA"
)


class Command(BaseCommand):
    help = "Seed the library with dummy categories, authors and books."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=150)

    def handle(self, *args, **options):
        count = options["count"]

        categories = []
        for name, icon in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={"icon": icon, "description": f"{name} books curated for you."}
            )
            categories.append(cat)
        self.stdout.write(self.style.SUCCESS(f"✓ {len(categories)} categories ready"))

        authors = []
        used_names = set()
        while len(authors) < 40:
            name = f"{random.choice(AUTHOR_FIRST)} {random.choice(AUTHOR_LAST)}"
            if name in used_names:
                continue
            used_names.add(name)
            author, _ = Author.objects.get_or_create(
                name=name, defaults={"bio": f"{name} is a celebrated writer known for insightful, engaging books."}
            )
            authors.append(author)
        self.stdout.write(self.style.SUCCESS(f"✓ {len(authors)} authors ready"))

        created = 0
        used_titles = set()
        for i in range(1, count + 1):
            title = f"{random.choice(TITLE_WORDS_A)} {random.choice(TITLE_WORDS_B)}"
            if title in used_titles:
                title = f"{title} {i}"
            used_titles.add(title)

            slug = slugify(title)
            if Book.objects.filter(slug=slug).exists():
                continue

            author = random.choice(authors)
            category = random.choice(categories)
            language = random.choice(LANGUAGES)
            is_free = random.random() < 0.25
            price = 0 if is_free else round(random.uniform(3, 45), 2)
            has_discount = (not is_free) and random.random() < 0.3
            discount_price = round(price * random.uniform(0.5, 0.85), 2) if has_discount else None
            pages = random.randint(80, 480)
            has_audio = random.random() < 0.55
            pub_date = date.today() - timedelta(days=random.randint(0, 365 * 6))

            book = Book(
                title=title,
                slug=slug,
                author=author,
                category=category,
                description=(
                    f"{title} by {author.name} is a compelling {category.name.lower()} book "
                    f"spanning {pages} pages. A must-read for anyone interested in {category.name.lower()}."
                ),
                short_description=f"A compelling {category.name.lower()} book by {author.name}.",
                language=language,
                pages=pages,
                isbn=f"978-{random.randint(1000000000, 9999999999)}",
                published_date=pub_date,
                price=price,
                discount_price=discount_price,
                preview_pages=min(15, pages),
                is_featured=random.random() < 0.2,
                is_free=is_free,
                is_published=True,
                is_bestseller=random.random() < 0.15,
                views_count=random.randint(0, 5000),
                downloads_count=random.randint(0, 800),
            )

            color = random.choice(SVG_PALETTE)
            book.cover.save(f"{slug}.svg", ContentFile(make_cover_svg(title, color)), save=False)
            book.pdf_file.save(f"{slug}.pdf", ContentFile(MINI_PDF), save=False)
            if has_audio:
                book.audio_file.save(f"{slug}.mp3", ContentFile(MINI_MP3), save=False)

            book.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(f"✓ {created} books created"))
        self.stdout.write(self.style.SUCCESS("Seeding complete. Run `python manage.py createsuperuser` "
                                              "then log in with a staff account to use /dashboard/."))
