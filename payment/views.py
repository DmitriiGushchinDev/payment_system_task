from decimal import ROUND_HALF_UP, Decimal
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Item, Order, OrderItem, Discount, Tax
from django.shortcuts import redirect,get_object_or_404
# Create your views here.
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
import stripe
import requests



@csrf_exempt
def create_payment_intent(request, item_id):
    # Retrieve the item by ID
    item = get_object_or_404(Item, id=item_id)
    currency = item.currency

    # Set the appropriate Stripe secret key based on currency
    stripe.api_key = settings.STRIPE_SECRET_KEY.get(currency)

    if stripe.api_key is None:
        return JsonResponse({'error': f'Stripe key not found for currency "{currency}"'}, status=500)

    try:
        # Create the payment intent
        intent = stripe.PaymentIntent.create(
            amount=int(item.price * 100),  # price in cents
            currency=currency,
            payment_method_types=['card'],
            metadata={
                'item_id': str(item.id),
                'item_name': item.name,
                'currency': currency,
            },
        )

        context = {
            'item': item,
            'clientSecret': intent.client_secret,
            'publishableKey': settings.STRIPE_PUBLISHABLE_KEY.get(currency),
        }

        return render(request, 'payment/intent_payment.html', context)

    except stripe.error.StripeError as e:
        # Handle Stripe-specific errors
        return JsonResponse({'error': str(e)}, status=400)

    except Exception as e:
        # Handle unexpected errors
        return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)# @login_required
    

def CreateCheckoutSessionView(request, item_id):
    item= Item.objects.get(id=item_id)
    selected_currency = request.GET.get('currency', item.currency.lower())
    currency = selected_currency
    if currency=='eur':
        response = requests.get("https://api.exchangerate.host/convert", params={
        "access_key":"4e893d67f180834c6629e9db1a5fde7b",
        "from": "USD",
        "to": "EUR",
        "amount": item.price
    })
        data=response.json()
        if not data.get("result"):
            raise Exception(f"Currency conversion failed: {data}")
        print (data)
        price=data['result']
    else:
        price=item.price
    stripe.api_key = settings.STRIPE_SECRET_KEY[currency]
    YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
    
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': currency,
                    'unit_amount': int(price*100),
                    'product_data': {
                        'name': item.name
                        # 'images': [f'{item.image}']
                    },
                },
                'quantity': 1,
            },
        ],
        metadata = {
            'item_id': item_id,
            # 'user_email': request.user.email
        },
        
        mode='payment',

        success_url=YOUR_DOMAIN + f'/payment-success/',
        cancel_url=YOUR_DOMAIN + f'/payment-cancel',
    )

    return redirect(checkout_session.url)


def CreateCheckoutForOrderView(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY['usd']
    total_price = 0
    order_items = OrderItem.objects.all()
    for order in order_items:
        total_price += order.item.price * order.quantity
    tax= Tax.objects.first()  
    discount = Discount.objects.first() 
    order = Order.objects.create(total_price=total_price, tax=tax, discount=discount)
    tax_amount=((order.tax.percentage/100) * order.total_price)
    print(tax_amount)
    discount_amount = (order.discount.percentage/100)
    YOUR_DOMAIN = f"{request.scheme}://{request.get_host()}"
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(order.total_price * 100),
                    'product_data': {
                        'name': 'Your Order',
                        # 'tax_code': 'txcd_99999999'
                    },
                },
                'quantity': 1,
            },
             {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(((order.tax.percentage/100+1) * order.total_price*100)-(order.total_price * 100)),
                    'product_data': {
                        'name': 'Tax amount',
                        # 'tax_code': 'txcd_99999999'
                    },
                },
                'quantity': 1,

            },
        ],
        discounts=[{
            'coupon': discount.code if discount else None
        }],

        metadata = {
            'item_id': order.id,
            # 'user_email': request.user.email
        },
        
        mode='payment',

        success_url=YOUR_DOMAIN + f'/payment-success/',
        cancel_url=YOUR_DOMAIN + f'/payment-cancel',
    )
    order.delete()
    return redirect(checkout_session.url)


def payment_success(request):
    order_items=OrderItem.objects.all()
    for order in order_items:
        order.delete()
    return render(request, 'payment/payment_success.html')

def payment_cancel(request):
    return render(request, 'payment/payment_cancel.html')


def item_list(request):
    items = Item.objects.all()
    return render(request, 'payment/items_list.html', {'items': items})

def item_detail(request, item_id):
    item = Item.objects.get(id=item_id)
    return render(request, 'payment/item_details.html', {'item': item})

def add_to_cart(request, item_id):
    item = Item.objects.get(id=item_id)
    order_item, created = OrderItem.objects.get_or_create(item=item)
    if created:
        order_item.quantity = 1
    else:
        order_item.quantity += 1
    order_item.save()
    return redirect('payment:item_detail', item_id=item.id)

def cart_view(request):
    order_items = OrderItem.objects.all()
    total_price = sum(order_item.item.price * order_item.quantity for order_item in order_items)
    return render(request, 'payment/cart.html', {'order_items': order_items, 'total_price': total_price})

