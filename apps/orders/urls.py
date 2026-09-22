from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/<int:book_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:book_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:book_id>/', views.cart_update, name='cart_update'),
    path('cart/coupon/apply/', views.apply_coupon, name='apply_coupon'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='success'),
    path('<int:order_id>/', views.order_detail, name='detail'),
]
