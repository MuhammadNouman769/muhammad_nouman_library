from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='list'),
    path('featured/', views.featured_books, name='featured'),
    path('latest/', views.latest_books, name='latest'),
    path('popular/', views.popular_books, name='popular'),
    path('free/', views.free_books, name='free'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<slug:slug>/', views.author_detail, name='author_detail'),
    path('search/live/', views.live_search, name='live_search'),
    path('<slug:slug>/', views.book_detail, name='detail'),
    path('<slug:slug>/preview/', views.book_preview, name='preview'),
    path('<slug:slug>/wishlist/toggle/', views.toggle_wishlist, name='toggle_wishlist'),
    path('<slug:slug>/review/', views.submit_review, name='submit_review'),
]
