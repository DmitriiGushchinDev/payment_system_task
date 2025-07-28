from django.urls import path
from . import  views 


app_name = 'payment'  
urlpatterns = [
    path('', views.item_list, name='item_list'),  
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('buy/<int:item_id>/', views.CreateCheckoutSessionView, name='create_checkout_session'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('buy_order/', views.CreateCheckoutForOrderView, name='buy_order'), 
    path('stripe-payment-intent/<int:item_id>/',views.create_payment_intent,name='payment_intent') 
    # path('cart/', views.cart_view, name='cart_view
]
