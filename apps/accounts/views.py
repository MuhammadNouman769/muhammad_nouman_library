from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from apps.books.models import Wishlist
from apps.orders.models import Order

from .forms import ProfileForm, SignUpForm, UserUpdateForm


class AccountLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class AccountLogoutView(LogoutView):
    next_page = 'core:home'


def signup(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.first_name}! Your account has been created.")
            return redirect('core:home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileForm(instance=request.user.profile)
    return render(request, 'accounts/profile.html', {'u_form': u_form, 'p_form': p_form})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/my_orders.html', {'orders': orders})


@login_required
def my_wishlist(request):
    items = Wishlist.objects.filter(user=request.user).select_related('book')
    return render(request, 'accounts/my_wishlist.html', {'items': items})


@login_required
def my_downloads(request):
    from apps.orders.models import OrderItem
    items = OrderItem.objects.filter(order__user=request.user, order__status='completed').select_related('book')
    return render(request, 'accounts/my_downloads.html', {'items': items})
