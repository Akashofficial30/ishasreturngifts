from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Cart, CartItem
from .models import Order, OrderItem
from .email_utils import send_order_confirmation_email, send_admin_order_notification


@login_required(login_url='/users/login/')
def checkout(request):
    if not request.session.session_key:
        return redirect('cart')
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if not cart or cart.get_item_count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    cart_items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'user': request.user,
    }
    return render(request, 'orders/checkout.html', context)


@login_required(login_url='/users/login/')
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')
    if not request.session.session_key:
        return redirect('cart')
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if not cart or cart.get_item_count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    payment_method = request.POST.get('payment_method', 'online')
    order = Order.objects.create(
        customer_name=request.POST.get('name'),
        customer_email=request.POST.get('email', ''),
        customer_phone=request.POST.get('phone'),
        address=request.POST.get('address'),
        city=request.POST.get('city'),
        state=request.POST.get('state', 'Tamil Nadu'),
        pincode=request.POST.get('pincode'),
        total_price=cart.get_total(),
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending',
    )

    for item in cart.items.select_related('product').all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_name=item.product.name,
            product_price=item.product.effective_price,
            quantity=item.quantity,
        )

    if payment_method == 'cod':
        order.payment_status = 'pending'
        order.order_status = 'confirmed'
        order.save()
        Cart.objects.filter(session_key=request.session.session_key).delete()
        send_order_confirmation_email(order)
        send_admin_order_notification(order)
        return redirect('order_confirmation', order_id=order.id)

    request.session['pending_order_id'] = order.id
    return redirect('initiate_payment', order_id=order.id)


@login_required(login_url='/users/login/')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/order_confirmation.html', {'order': order})
