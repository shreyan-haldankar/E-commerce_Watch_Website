from unicodedata import name
from django.urls import path, include
from .views import (add_to_cart,remove_from_cart, OrderSummaryView ,CheckoutView, PaymentView , HomeView, ProductsView, ItemDetailView, remove_single_item_from_cart)

urlpatterns = [
    
    path('', HomeView, name="home"),

    path('products/', ProductsView.as_view(), name="products"),
    path('product/<slug>/', ItemDetailView.as_view(), name="product"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),

    path('payment/<payment_option>/', PaymentView.as_view(), name="payment"),

    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),

    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>/', remove_from_cart, name="remove-from-cart"),

    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name="remove-single-item-from-cart"),

    
    
]