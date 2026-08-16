import razorpay
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from orders.models import Order
from orders.email_utils import send_order_confirmation_email, send_admin_order_notification
from products.models import Cart
from .models import Payment
from django.http import HttpResponseNotFound


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def initiate_latest(request):
    """Debug helper: redirect to initiate_payment for the newest Order.
    Only active when `settings.DEBUG` is True to avoid exposing in production.
    """
    if not getattr(settings, 'DEBUG', False):
        return HttpResponseNotFound('Not found')

    latest = Order.objects.order_by('-id').first()
    if not latest:
        return HttpResponseNotFound('No orders available')

    return redirect('initiate_payment', order_id=latest.id)


def initiate_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    client = get_razorpay_client()

    amount_paise = int(order.total_price * 100)

    # include preferred online channel (card/upi/qr) from session if present
    preferred_channel = request.session.pop('online_channel', None)

    notes = {
        'customer_name': order.customer_name,
        'customer_phone': order.customer_phone,
    }
    if preferred_channel:
        notes['preferred_channel'] = preferred_channel

    razorpay_order = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'receipt': str(order.order_id),
        'notes': notes
    })

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
        'preferred_channel': preferred_channel,
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
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'paid'
            payment.save()

            order = payment.order
            order.payment_id = razorpay_payment_id
            order.payment_status = 'paid'
            order.order_status = 'confirmed'
            order.save()

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
