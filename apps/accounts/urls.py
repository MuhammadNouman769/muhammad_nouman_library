from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.AccountLoginView.as_view(), name='login'),
    path('logout/', views.AccountLogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('orders/', views.my_orders, name='my_orders'),
    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    path('downloads/', views.my_downloads, name='my_downloads'),
]
