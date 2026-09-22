# Muhammad Nouman Library

Industry-style Django online library / bookstore — read online, download PDFs,
listen to audiobooks, order books, and manage everything from a **custom
staff dashboard** (Django's built-in `/admin/` is not used for site management).

## Features

- Public site: Home, About, All Books, Book Detail, Categories, Featured/Latest/Popular/Free
  Books, Authors, Audio Books, Book Preview, Search, Advanced Filters, Contact, FAQ,
  Privacy Policy, Terms of Use, Refund Policy, Shipping Policy, Copyright, 404/500.
- Book detail: cover, description, language, pages, ISBN, price, PDF download,
  online reading preview, audio player, related books, add to cart, buy now,
  wishlist, reviews & ratings.
- Cart & checkout: session-based cart (works before login), coupon codes,
  order creation, order history/downloads — all via AJAX, no page reloads.
- Custom dashboard (`/dashboard/`, staff-only): Overview (stats), Books (add/edit/delete),
  Categories, Authors, Orders (status updates), Customers, Audio Books, Downloads,
  Reviews moderation, Coupons, Reports, Website Settings, Profile.
- Language switcher: English / Urdu / Arabic (Django i18n) — see note below.
- 150 dummy books auto-generated with real cover images, real PDFs and (for ~40%)
  a real playable audio file, via a management command.

## Setup

```bash
python -m venv venv
source venv/bin/activate          # venv\Scripts\activate on Windows

pip install -r requirements.txt

cp .env.example .env               # already has sensible local defaults

python manage.py migrate
python manage.py createsuperuser   # tick "staff status" — this account can use /dashboard/

# Seed ~150 dummy books with generated covers, PDFs and audio files:
python manage.py seed_library
# (Faster, no generated files: python manage.py seed_library --skip-files)

python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Log in with your superuser account and open
`http://127.0.0.1:8000/dashboard/` to manage the store.

## Notes

- **Language switcher**: the switcher itself works immediately (it changes the
  active Django language via `django.middleware.locale.LocaleMiddleware`), but
  actual Urdu/Arabic *translations* of the UI text need `.po`/`.mo` files, which
  require the `gettext` tool:
  ```bash
  django-admin makemessages -l ur -l ar
  # ...translate the .po files under locale/...
  django-admin compilemessages
  ```
  Until you do that, switching language changes `dir="rtl"` etc. but text stays English.
- Payments: no payment gateway is wired up yet, matching the original scope —
  orders are created directly from checkout. Add JazzCash/Easypaisa/Stripe later
  inside `apps/orders/views.checkout`.
- Media files (covers, PDFs, audio) are served from `/media/` in development
  (`DEBUG=True`). Configure a proper media host (S3, etc.) for production.
- The generated PDFs/audio from `seed_library` are placeholders (short real
  PDFs with a few pages of text, and short silent audio clips) so every button
  and player genuinely works — swap in real files by re-uploading through the
  dashboard's Edit Book page.

## Project structure

```
muhammad_nouman_library/
├── core/                  # settings, urls, wsgi/asgi
├── apps/
│   ├── books/             # Book, Author, Review, Wishlist + views/forms
│   ├── categories/        # Category
│   ├── accounts/          # signup/login/profile (Django auth + Profile)
│   ├── orders/            # cart, checkout, Order/OrderItem, Coupon
│   ├── dashboard/         # custom staff dashboard (replaces admin)
│   ├── audio/             # audiobook listing + player endpoint
│   ├── pages/             # about/contact/faq/legal pages
│   └── core/              # home page + error handlers
├── templates/             # all HTML templates, organized per app
├── static/{css,js}/       # style.css, main.js (all AJAX behaviour)
├── media/{covers,books,audio}/  # uploaded/generated files
└── fixtures/              # (optional) exported fixtures
```
