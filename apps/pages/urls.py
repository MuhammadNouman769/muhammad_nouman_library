from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-use/', views.terms_of_use, name='terms_of_use'),
    path('refund-policy/', views.refund_policy, name='refund_policy'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('copyright/', views.copyright_page, name='copyright'),
]
