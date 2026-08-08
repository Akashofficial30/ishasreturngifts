import logging

import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from orders.models import Order
from orders.views import may_view_order, remember_own_order
from orders.email_utils import send_order_confirmation_email, send_admin_order_notification
from products.models import Cart
from .models import Payment

logger = logging.getLogger(__name__)


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required(login_url='/users/login/')
def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Was reachable by anyone, for any order id — it renders the customer's
    # details and creates a real gateway order on every call.
    if not may_view_order(request, order):
        raise Http404
    if order.payment_status == 'paid':
        messages.info(request, 'This order has already been paid for.')
        return redirect('order_confirmation', order_id=order.id)
    client = get_razorpay_client()

    amount_paise = int(order.total_price * 100)

    # The order row already exists at this point, so a gateway failure must not
    # surface as a 500 — the customer would be left staring at a crash with an
    # order silently sitting in the database.
    try:
        razorpay_order = client.order.create({
            'amount': amount_paise,
            'currency': 'INR',
            'receipt': str(order.order_id),
            'notes': {
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
            }
        })
    except Exception:
        logger.exception('Razorpay order creation failed for order %s', order.id)
        order.order_status = 'pending'
        order.notes = f'{order.notes}\nPayment gateway unreachable at checkout.'.strip()
        order.save(update_fields=['order_status', 'notes'])
        messages.error(
            request,
            'We could not reach the payment gateway. Your order has been saved — '
            'please contact us on WhatsApp with your order ID to complete payment.'
        )
        return redirect('order_confirmation', order_id=order.id)

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    Payment.objects.update_or_create(
        order=order,
        defaults={
            'razorpay_order_id': razorpay_order['id'],
            'amount': order.total_price,
            'status': 'created',
        }
    )

    context = {
        'order': order,
        'razorpay_order_id': razorpay_order['id'],
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'amount_paise': amount_paise,
        'amount': order.total_price,
    }
    return render(request, 'payments/payment.html', context)


@csrf_exempt
def payment_success(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        client = get_razorpay_client()
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Payment verification failed. Please contact support.')
            return redirect('home')

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            order = payment.order

            # Idempotent: Razorpay can deliver this more than once, and the
            # customer can refresh. Without this the confirmation emails were
            # re-sent on every replay.
            if payment.status == 'paid' and order.payment_status == 'paid':
                remember_own_order(request, order)
                return redirect('order_confirmation', order_id=order.id)

            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'paid'
            payment.save()

            order.payment_id = razorpay_payment_id
            order.payment_status = 'paid'
            order.order_status = 'confirmed'
            order.save()
            remember_own_order(request, order)

            # Clear cart
            if request.session.session_key:
                Cart.objects.filter(session_key=request.session.session_key).delete()

            # Send confirmation email to customer
            send_order_confirmation_email(order)

            # Send notification email to admin
            send_admin_order_notification(order)

            return redirect('order_confirmation', order_id=order.id)

        except Payment.DoesNotExist:
            messages.error(request, 'Payment record not found.')
            return redirect('home')

    return redirect('home')


@csrf_exempt
def payment_failed(request):
    return render(request, 'payments/payment_failed.html')
