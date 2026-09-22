from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.overview, name='overview'),

    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_add, name='book_add'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('authors/', views.author_list, name='author_list'),
    path('authors/add/', views.author_add, name='author_add'),

    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),

    path('customers/', views.customer_list, name='customer_list'),
    path('audiobooks/', views.audiobook_list, name='audiobook_list'),
    path('downloads/', views.download_list, name='download_list'),

    path('reviews/', views.review_list, name='review_list'),
    path('reviews/<int:pk>/toggle/', views.review_toggle, name='review_toggle'),

    path('coupons/', views.coupon_list, name='coupon_list'),
    path('coupons/add/', views.coupon_add, name='coupon_add'),

    path('reports/', views.reports, name='reports'),
    path('settings/', views.website_settings, name='settings'),
    path('profile/', views.dashboard_profile, name='profile'),
]
