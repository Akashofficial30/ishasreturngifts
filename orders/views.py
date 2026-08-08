from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from products.models import Cart, Product
from .models import Order, OrderItem
from .email_utils import send_order_confirmation_email, send_admin_order_notification

# Fields the customer must supply. state has a model default; email is optional.
REQUIRED_FIELDS = {
    'name': 'full name',
    'phone': 'phone number',
    'address': 'delivery address',
    'city': 'city',
    'pincode': 'PIN code',
}


class OutOfStock(Exception):
    """Raised inside the checkout transaction so the order rolls back."""

    def __init__(self, names):
        self.names = names
        super().__init__(', '.join(names))


def remember_own_order(request, order):
    """Record an order as belonging to this session.

    Ownership is normally established by order.user; this also covers orders
    placed before that field existed.
    """
    owned = request.session.get('own_order_ids', [])
    if order.id not in owned:
        owned.append(order.id)
        request.session['own_order_ids'] = owned


def may_view_order(request, order):
    if request.user.is_staff:
        return True
    if order.user_id and order.user_id == request.user.id:
        return True
    return order.id in request.session.get('own_order_ids', [])


@login_required(login_url='/users/login/')
def checkout(request):
    if not request.session.session_key:
        return redirect('cart')
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if not cart or cart.get_item_count() == 0:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')
    cart_items = cart.items.select_related('product').all()
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'cart_items': cart_items,
        'user': request.user,
    })


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

    # Validate before writing anything — these columns are NOT NULL, so a
    # missing field previously surfaced as an IntegrityError mid-checkout.
    values = {field: (request.POST.get(field) or '').strip() for field in REQUIRED_FIELDS}
    missing = [label for field, label in REQUIRED_FIELDS.items() if not values[field]]
    if missing:
        messages.error(request, f"Please enter your {', '.join(missing)}.")
        return redirect('checkout')

    payment_method = request.POST.get('payment_method', 'online')
    if payment_method not in dict(Order.PAYMENT_METHOD_CHOICES):
        payment_method = 'online'

    try:
        order = _create_order(request, cart, values, payment_method)
    except OutOfStock as exc:
        messages.error(
            request,
            f"Sorry, we no longer have enough stock for: {', '.join(exc.names)}. "
            'Please adjust your cart and try again.'
        )
        return redirect('cart')

    remember_own_order(request, order)

    if payment_method == 'cod':
        order.payment_status = 'pending'
        order.order_status = 'confirmed'
        order.save(update_fields=['payment_status', 'order_status'])
        Cart.objects.filter(session_key=request.session.session_key).delete()
        send_order_confirmation_email(order)
        send_admin_order_notification(order)
        # COD is settled on delivery — it must not reach the payment gateway.
        return redirect('order_confirmation', order_id=order.id)

    request.session['pending_order_id'] = order.id
    return redirect('initiate_payment', order_id=order.id)


@transaction.atomic
def _create_order(request, cart, values, payment_method):
    """Create the order and its items, decrementing stock atomically.

    The product rows are locked for the duration so two simultaneous checkouts
    cannot both pass the stock check and oversell the same item. Prices are
    read from the locked product rows, never from the client.
    """
    cart_items = list(cart.items.select_related('product').all())
    locked = Product.objects.select_for_update().filter(
        id__in=[item.product_id for item in cart_items]
    )
    products = {product.id: product for product in locked}

    short = [
        products[item.product_id].name
        for item in cart_items
        if products[item.product_id].stock_quantity < item.quantity
    ]
    if short:
        raise OutOfStock(short)

    total = sum(
        products[item.product_id].effective_price * item.quantity
        for item in cart_items
    )

    order = Order.objects.create(
        user=request.user,
        customer_name=values['name'],
        customer_email=(request.POST.get('email') or '').strip(),
        customer_phone=values['phone'],
        address=values['address'],
        city=values['city'],
        state=(request.POST.get('state') or '').strip() or 'Tamil Nadu',
        pincode=values['pincode'],
        total_price=total,
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending',
    )

    for item in cart_items:
        product = products[item.product_id]
        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_price=product.effective_price,
            quantity=item.quantity,
        )
        product.stock_quantity -= item.quantity
        product.save(update_fields=['stock_quantity'])

    return order


@login_required(login_url='/users/login/')
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if not may_view_order(request, order):
        raise Http404
    return render(request, 'orders/order_confirmation.html', {'order': order})
