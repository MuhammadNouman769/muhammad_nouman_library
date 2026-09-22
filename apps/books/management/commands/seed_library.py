"""
Seeds the library with categories, authors and ~150 dummy books.
Generates real placeholder files so every feature (cover, PDF download,
audio player) works out of the box:
  - Cover images -> Pillow (drawn cover with title/author)
  - PDF files    -> reportlab (a real multi-page PDF per book)
  - Audio files  -> stdlib `wave` module (a short silent .wav per audiobook)

Run with:  python manage.py seed_library
Add --flush to wipe existing Books/Authors/Categories first.
"""
import io
import random
import struct
import wave
from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.books.models import Author, Book
from apps.categories.models import Category

CATEGORIES = [
    ("Fiction", "bi-book"),
    ("Non-Fiction", "bi-journal-text"),
    ("Science", "bi-atom"),
    ("Business & Finance", "bi-graph-up-arrow"),
    ("Self-Help", "bi-lightbulb"),
    ("History", "bi-hourglass-split"),
    ("Biography", "bi-person-badge"),
    ("Technology", "bi-cpu"),
    ("Poetry", "bi-feather"),
    ("Religion & Spirituality", "bi-moon-stars"),
    ("Children", "bi-emoji-smile"),
    ("Romance", "bi-heart"),
]

FIRST_NAMES = [
    "Ahmed", "Sara", "Bilal", "Ayesha", "Hassan", "Fatima", "Usman", "Zainab",
    "Ali", "Mariam", "Omar", "Hina", "Imran", "Sana", "Kamran", "Nida",
    "Tariq", "Rabia", "Salman", "Amna", "Farhan", "Iqra", "Adeel", "Noor",
    "James", "Emily", "Michael", "Sophia", "Daniel", "Olivia", "Ryan", "Grace",
]
LAST_NAMES = [
    "Khan", "Malik", "Siddiqui", "Raza", "Farooq", "Chaudhry", "Sheikh", "Baig",
    "Qureshi", "Abbasi", "Hussain", "Iqbal", "Anderson", "Carter", "Bennett",
    "Wallace", "Mitchell", "Hughes",
]

TITLE_TEMPLATES = [
    "The {adj} {noun}", "A {adj} Journey Through {noun}", "{noun} and {noun2}",
    "The Art of {noun}", "Whispers of {noun}", "The Last {noun}", "Rise of the {noun}",
    "{adj} Minds", "The {noun} Within", "Shadows Over {noun}", "The Complete Guide to {noun}",
    "Mastering {noun}", "{noun}: A New Beginning", "The Secret {noun}", "Beyond {noun}",
    "The {adj} Path", "Echoes of {noun}", "The {noun} Chronicles", "Understanding {noun}",
    "The Power of {noun}",
]
ADJ = ["Silent", "Golden", "Hidden", "Broken", "Endless", "Forgotten", "Bright",
       "Modern", "Ancient", "Quiet", "Radical", "Practical", "Essential", "Timeless"]
NOUN = ["River", "Mountains", "Mind", "Empire", "Garden", "Stars", "City", "Ocean",
        "Code", "Markets", "Leadership", "Innovation", "Freedom", "Wisdom", "Dreams",
        "Strategy", "Destiny", "Kingdom", "Horizon", "Legacy", "Universe", "Growth"]

LOREM = (
    "This chapter explores the central ideas of the book, weaving together "
    "narrative and insight to guide the reader through a compelling argument. "
    "Each section builds on the last, offering practical examples and thoughtful "
    "reflection. Readers will find both inspiration and clarity within these pages, "
    "as the author draws on years of research and lived experience to make the "
    "case for a deeper understanding of the subject at hand."
)


def make_title(used):
    while True:
        t = random.choice(TITLE_TEMPLATES).format(
            adj=random.choice(ADJ), noun=random.choice(NOUN), noun2=random.choice(NOUN)
        )
        if t not in used:
            used.add(t)
            return t


def make_cover_bytes(title, author, seed):
    from PIL import Image, ImageDraw, ImageFont

    random.seed(seed)
    colors = [(28, 43, 74), (18, 90, 100), (120, 40, 90), (60, 90, 40), (100, 60, 20)]
    bg = random.choice(colors)
    img = Image.new("RGB", (600, 840), bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, 599, 839], outline=(224, 165, 39), width=6)

    try:
        font_title = ImageFont.load_default()
    except Exception:
        font_title = None

    words = title.split()
    lines, line = [], ""
    for w in words:
        if len(line + " " + w) > 18:
            lines.append(line)
            line = w
        else:
            line = (line + " " + w).strip()
    lines.append(line)

    y = 320
    for line in lines:
        draw.text((50, y), line, fill=(255, 255, 255), font=font_title)
        y += 28

    draw.text((50, y + 40), f"by {author}", fill=(224, 165, 39), font=font_title)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def make_pdf_bytes(title, author, pages):
    from reportlab.lib.pagesizes import A5
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A5)
    width, height = A5

    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 100, title)
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 130, f"by {author}")
    c.showPage()

    body_pages = min(max(pages // 30, 3), 8)
    for i in range(body_pages):
        c.setFont("Helvetica-Bold", 13)
        c.drawString(40, height - 50, f"Chapter {i + 1}")
        c.setFont("Helvetica", 10)
        text = c.beginText(40, height - 80)
        text.setLeading(14)
        for _ in range(6):
            for chunk in [LOREM[j:j + 85] for j in range(0, len(LOREM), 85)]:
                text.textLine(chunk)
        c.drawText(text)
        c.showPage()

    c.save()
    return buf.getvalue()


def make_silent_wav_bytes(seconds=2):
    n_channels, sampwidth, framerate = 1, 2, 22050
    n_frames = seconds * framerate
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(n_channels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(framerate)
        silence = struct.pack("<h", 0) * n_frames
        wf.writeframes(silence)
    return buf.getvalue()


class Command(BaseCommand):
    help = "Seed the library with categories, authors and ~150 dummy books."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=150)
        parser.add_argument("--flush", action="store_true", help="Delete existing books/authors/categories first")
        parser.add_argument("--skip-files", action="store_true", help="Skip generating cover/PDF/audio files (faster)")

    def handle(self, *args, **options):
        count = options["count"]
        if options["flush"]:
            Book.objects.all().delete()
            Author.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing books, authors, categories."))

        categories = []
        for name, icon in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"icon": icon, "description": f"{name} books"})
            categories.append(cat)

        authors = []
        used_names = set()
        while len(authors) < 40:
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            if name in used_names:
                continue
            used_names.add(name)
            author, _ = Author.objects.get_or_create(
                name=name, defaults={"bio": f"{name} is an author writing across multiple genres."}
            )
            authors.append(author)

        silent_wav = None if options["skip_files"] else make_silent_wav_bytes()
        used_titles = set()
        created = 0

        for i in range(count):
            title = make_title(used_titles)
            author = random.choice(authors)
            category = random.choice(categories)
            language = random.choices(["en", "ur", "ar"], weights=[75, 15, 10])[0]
            pages = random.randint(80, 480)
            price = round(random.choice([0, 299, 399, 499, 599, 799, 999, 1299]), 2)
            is_free = price == 0
            has_discount = (not is_free) and random.random() < 0.3
            discount_price = round(price * random.uniform(0.6, 0.85), 2) if has_discount else None
            published_date = date.today() - timedelta(days=random.randint(30, 8 * 365))

            book = Book(
                title=title,
                author=author,
                category=category,
                description=(LOREM + " ") * 3,
                short_description=f"A compelling read about {title.split()[-1].lower()} and the human experience.",
                language=language,
                pages=pages,
                isbn=f"978-{random.randint(1000000000, 9999999999)}",
                published_date=published_date,
                price=price,
                discount_price=discount_price,
                preview_pages=min(10, pages // 4 or 1),
                is_featured=random.random() < 0.15,
                is_free=is_free,
                is_published=True,
                is_bestseller=random.random() < 0.12,
                views_count=random.randint(0, 5000),
                downloads_count=random.randint(0, 800),
            )

            if not options["skip_files"]:
                try:
                    cover_bytes = make_cover_bytes(title, author.name, seed=i)
                    book.cover.save(f"{book.slug or i}-cover.jpg", ContentFile(cover_bytes), save=False)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Cover skipped for '{title}': {e}"))

                try:
                    pdf_bytes = make_pdf_bytes(title, author.name, pages)
                    book.pdf_file.save(f"{book.slug or i}.pdf", ContentFile(pdf_bytes), save=False)
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"PDF skipped for '{title}': {e}"))

                if silent_wav and random.random() < 0.4:
                    book.audio_file.save(f"{book.slug or i}.wav", ContentFile(silent_wav), save=False)

            book.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {created} books, {len(authors)} authors, {len(categories)} categories."
        ))
        self.stdout.write(self.style.SUCCESS(
            "Tip: run with --skip-files for an instant seed without generating cover/PDF/audio files."
        ))
