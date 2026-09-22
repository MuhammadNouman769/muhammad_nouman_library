from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # language switch (set_language)
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('orders/', include('apps.orders.urls', namespace='orders')),
    path('audio/', include('apps.audio.urls', namespace='audio')),
    path('books/', include('apps.books.urls', namespace='books')),
    path('category/', include('apps.categories.urls', namespace='categories')),
    path('', include('apps.pages.urls', namespace='pages')),
    path('', include('apps.core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'apps.core.views.error_404'
handler500 = 'apps.core.views.error_500'
