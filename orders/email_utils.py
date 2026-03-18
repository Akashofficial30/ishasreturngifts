from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_order_confirmation_email(order):
    """Send beautiful HTML invoice email to customer after payment"""

    if not order.customer_email:
        print("[Email] No customer email provided — skipping customer email.")
        return

    # Build order items rows
    items_html = ""
    items_text = ""
    for item in order.items.all():
        items_html += f"""
        <tr>
            <td style="padding:12px 16px;border-bottom:1px solid #f0e8d8;font-family:Arial,sans-serif;font-size:14px;color:#4a3820;">{item.product_name}</td>
            <td style="padding:12px 16px;border-bottom:1px solid #f0e8d8;font-family:Arial,sans-serif;font-size:14px;color:#4a3820;text-align:center;">{item.quantity}</td>
            <td style="padding:12px 16px;border-bottom:1px solid #f0e8d8;font-family:Arial,sans-serif;font-size:14px;color:#4a3820;text-align:right;">&#8377;{item.product_price}</td>
            <td style="padding:12px 16px;border-bottom:1px solid #f0e8d8;font-family:Arial,sans-serif;font-size:14px;font-weight:700;color:#6b1f2a;text-align:right;">&#8377;{item.get_subtotal()}</td>
        </tr>"""
        items_text += f"  {item.product_name} x{item.quantity} = Rs.{item.get_subtotal()}\n"

    subject = f"Order Confirmed #{order.get_short_order_id()} | Isha Return Gifts"

    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#fdf8f0;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf8f0;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

  <!-- HEADER -->
  <tr>
    <td style="background:linear-gradient(135deg,#6b1f2a,#3d0e18);border-radius:12px 12px 0 0;padding:36px 40px;text-align:center;">
      <p style="margin:0 0 6px;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:rgba(255,255,255,0.55);">Premium Return Gifts</p>
      <h1 style="margin:0 0 20px;font-size:26px;font-weight:400;color:#fff;letter-spacing:1px;">&#10022; Isha Return Gifts</h1>
      <div style="background:rgba(255,255,255,0.1);border-radius:8px;padding:14px 24px;display:inline-block;">
        <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.6);letter-spacing:2px;text-transform:uppercase;">Order Confirmed</p>
        <p style="margin:4px 0 0;font-size:22px;font-weight:700;color:#e8c97a;letter-spacing:2px;">#{order.get_short_order_id()}</p>
      </div>
    </td>
  </tr>

  <!-- SUCCESS BAR -->
  <tr>
    <td style="background:#f0faf0;padding:16px 40px;text-align:center;border-left:1px solid #e0d4b8;border-right:1px solid #e0d4b8;">
      <p style="margin:0;font-size:15px;color:#2e7d32;">
        &#127881; Thank you, <strong>{order.customer_name}</strong>! Your order is confirmed.
      </p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="background:#fff;padding:36px 40px;border-left:1px solid #e0d4b8;border-right:1px solid #e0d4b8;">

      <!-- Order Meta Grid -->
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr>
          <td width="50%" style="padding-right:8px;">
            <div style="background:#fdf8f0;border-radius:8px;padding:16px;border:1px solid #e8dcc4;">
              <p style="margin:0 0 4px;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#c9a84c;font-weight:700;">Order ID</p>
              <p style="margin:0;font-size:18px;font-weight:700;color:#1a1108;">#{order.get_short_order_id()}</p>
            </div>
          </td>
          <td width="50%" style="padding-left:8px;">
            <div style="background:#fdf8f0;border-radius:8px;padding:16px;border:1px solid #e8dcc4;">
              <p style="margin:0 0 4px;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#c9a84c;font-weight:700;">Payment ID</p>
              <p style="margin:0;font-size:12px;font-weight:600;color:#1a1108;word-break:break-all;">{order.payment_id}</p>
            </div>
          </td>
        </tr>
        <tr>
          <td width="50%" style="padding-right:8px;padding-top:10px;">
            <div style="background:#fdf8f0;border-radius:8px;padding:16px;border:1px solid #e8dcc4;">
              <p style="margin:0 0 4px;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#c9a84c;font-weight:700;">Payment Status</p>
              <p style="margin:0;font-size:15px;font-weight:700;color:#2e7d32;">&#10003; {order.payment_status.title()}</p>
            </div>
          </td>
          <td width="50%" style="padding-left:8px;padding-top:10px;">
            <div style="background:#fdf8f0;border-radius:8px;padding:16px;border:1px solid #e8dcc4;">
              <p style="margin:0 0 4px;font-size:10px;letter-spacing:2px;text-transform:uppercase;color:#c9a84c;font-weight:700;">Order Date</p>
              <p style="margin:0;font-size:13px;font-weight:600;color:#1a1108;">{order.created_at.strftime('%d %b %Y, %I:%M %p')}</p>
            </div>
          </td>
        </tr>
      </table>

      <!-- Items Table -->
      <h3 style="margin:0 0 14px;font-size:15px;font-weight:700;color:#1a1108;border-bottom:2px solid #c9a84c;padding-bottom:8px;">Items Ordered</h3>
      <table width="100%" cellpadding="0" cellspacing="0" style="border-radius:8px;overflow:hidden;border:1px solid #e8dcc4;margin-bottom:28px;">
        <thead>
          <tr style="background:#fdf8f0;">
            <th style="padding:10px 16px;text-align:left;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#8a7060;">Product</th>
            <th style="padding:10px 16px;text-align:center;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#8a7060;">Qty</th>
            <th style="padding:10px 16px;text-align:right;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#8a7060;">Price</th>
            <th style="padding:10px 16px;text-align:right;font-size:10px;letter-spacing:1.5px;text-transform:uppercase;color:#8a7060;">Total</th>
          </tr>
        </thead>
        <tbody>{items_html}</tbody>
        <tfoot>
          <tr style="background:#6b1f2a;">
            <td colspan="3" style="padding:14px 16px;font-size:14px;font-weight:700;color:#fff;text-align:right;">Total Amount Paid</td>
            <td style="padding:14px 16px;font-size:17px;font-weight:700;color:#e8c97a;text-align:right;">&#8377;{order.total_price}</td>
          </tr>
        </tfoot>
      </table>

      <!-- Delivery Address -->
      <div style="background:#fdf8f0;border-radius:8px;padding:20px 24px;border:1px solid #e8dcc4;margin-bottom:24px;">
        <h3 style="margin:0 0 12px;font-size:15px;font-weight:700;color:#1a1108;">Delivery Address</h3>
        <p style="margin:0 0 4px;font-size:14px;font-weight:600;color:#1a1108;">{order.customer_name}</p>
        <p style="margin:0 0 4px;font-size:13px;color:#4a3820;">{order.address}</p>
        <p style="margin:0 0 4px;font-size:13px;color:#4a3820;">{order.city}, {order.state} - {order.pincode}</p>
        <p style="margin:8px 0 0;font-size:13px;color:#4a3820;">Phone: {order.customer_phone}</p>
      </div>

      <!-- Note -->
      <div style="background:#fff8e6;border-radius:8px;padding:14px 18px;border-left:4px solid #c9a84c;">
        <p style="margin:0;font-size:13px;color:#8a6020;">
          <strong>What happens next?</strong> Our team will process and dispatch your order within 2-3 business days. You will receive a shipping update soon!
        </p>
      </div>

    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#1a1108;border-radius:0 0 12px 12px;padding:28px 40px;text-align:center;">
      <p style="margin:0 0 6px;font-size:15px;color:#c9a84c;font-weight:400;">&#10022; Isha Return Gifts</p>
      <p style="margin:0 0 12px;font-size:12px;color:rgba(255,255,255,0.45);">123, Gandhi Nagar, Chennai - 600001, Tamil Nadu</p>
      <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.35);">
        +91 98765 43210 &nbsp;|&nbsp; hello@ishareturnGifts.com
      </p>
      <p style="margin:14px 0 0;font-size:11px;color:rgba(255,255,255,0.25);">
        &copy; 2025 Isha Return Gifts. Made with love for your celebrations.
      </p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    text_content = f"""
ORDER CONFIRMED - Isha Return Gifts
====================================
Thank you, {order.customer_name}!

Order ID     : #{order.get_short_order_id()}
Payment ID   : {order.payment_id}
Status       : {order.payment_status.title()}
Date         : {order.created_at.strftime('%d %b %Y, %I:%M %p')}

ITEMS ORDERED
--------------
{items_text}
Total Paid   : Rs.{order.total_price}

DELIVERY ADDRESS
-----------------
{order.customer_name}
{order.address}
{order.city}, {order.state} - {order.pincode}
Phone: {order.customer_phone}

We will dispatch your order within 2-3 business days.

- Isha Return Gifts
  +91 98765 43210 | hello@ishareturnGifts.com
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.customer_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"[Email] ✅ Order confirmation sent to {order.customer_email}")
    except Exception as e:
        print(f"[Email] ❌ Failed to send customer email: {e}")
        print("[Email] Tip: Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py")


def send_admin_order_notification(order):
    """Send order alert to admin with full details"""

    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    if not admin_email or admin_email == 'your_gmail@gmail.com':
        print("[Email] Admin email not configured — skipping admin notification.")
        return

    items_html = ""
    items_text = ""
    for item in order.items.all():
        items_html += f"""
        <tr>
          <td style="padding:10px 14px;border-bottom:1px solid #f0e8d8;font-size:13px;color:#1a1108;">{item.product_name}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #f0e8d8;font-size:13px;text-align:center;">{item.quantity}</td>
          <td style="padding:10px 14px;border-bottom:1px solid #f0e8d8;font-size:13px;font-weight:700;color:#6b1f2a;text-align:right;">&#8377;{item.get_subtotal()}</td>
        </tr>"""
        items_text += f"  {item.product_name} x{item.quantity} = Rs.{item.get_subtotal()}\n"

    subject = f"New Order #{order.get_short_order_id()} - Rs.{order.total_price} | Isha Return Gifts"

    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:28px 16px;">
<tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e0d4b8;">

  <!-- HEADER -->
  <tr>
    <td style="background:#1a1108;padding:24px 32px;text-align:center;">
      <h2 style="margin:0;color:#c9a84c;font-weight:400;font-size:20px;">&#10022; Isha Return Gifts — Admin Alert</h2>
      <p style="margin:6px 0 0;color:rgba(255,255,255,0.5);font-size:12px;">New Order Received</p>
    </td>
  </tr>

  <!-- ALERT -->
  <tr>
    <td style="background:#fff8e6;padding:16px 32px;text-align:center;border-bottom:1px solid #e8dcc4;">
      <p style="margin:0;font-size:16px;color:#8a6020;">
        &#127881; New order of <strong>&#8377;{order.total_price}</strong> from <strong>{order.customer_name}</strong>
      </p>
    </td>
  </tr>

  <!-- BODY -->
  <tr>
    <td style="padding:28px 32px;">

      <!-- Order Info -->
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf8f0;border-radius:8px;padding:16px;border:1px solid #e8dcc4;margin-bottom:24px;">
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#8a7060;width:45%;">Order ID</td>
          <td style="padding:6px 0;font-size:13px;font-weight:700;color:#1a1108;text-align:right;">#{order.get_short_order_id()}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#8a7060;">Amount</td>
          <td style="padding:6px 0;font-size:16px;font-weight:700;color:#6b1f2a;text-align:right;">&#8377;{order.total_price}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#8a7060;">Payment ID</td>
          <td style="padding:6px 0;font-size:12px;font-weight:600;color:#1a1108;text-align:right;word-break:break-all;">{order.payment_id}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#8a7060;">Status</td>
          <td style="padding:6px 0;font-size:13px;font-weight:700;color:#2e7d32;text-align:right;">&#10003; {order.payment_status.title()}</td>
        </tr>
        <tr>
          <td style="padding:6px 0;font-size:13px;color:#8a7060;">Date</td>
          <td style="padding:6px 0;font-size:13px;color:#1a1108;text-align:right;">{order.created_at.strftime('%d %b %Y, %I:%M %p')}</td>
        </tr>
      </table>

      <!-- Customer -->
      <h3 style="margin:0 0 12px;font-size:14px;font-weight:700;color:#1a1108;border-bottom:2px solid #c9a84c;padding-bottom:6px;">Customer Details</h3>
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
        <tr>
          <td style="padding:5px 0;font-size:13px;color:#8a7060;width:40%;">Name</td>
          <td style="padding:5px 0;font-size:13px;font-weight:600;color:#1a1108;">{order.customer_name}</td>
        </tr>
        <tr>
          <td style="padding:5px 0;font-size:13px;color:#8a7060;">Phone</td>
          <td style="padding:5px 0;font-size:13px;font-weight:600;color:#1a1108;">{order.customer_phone}</td>
        </tr>
        <tr>
          <td style="padding:5px 0;font-size:13px;color:#8a7060;">Email</td>
          <td style="padding:5px 0;font-size:13px;color:#1a1108;">{order.customer_email or 'Not provided'}</td>
        </tr>
      </table>

      <!-- Shipping Address -->
      <h3 style="margin:0 0 12px;font-size:14px;font-weight:700;color:#1a1108;border-bottom:2px solid #c9a84c;padding-bottom:6px;">Shipping Address</h3>
      <div style="background:#fdf8f0;border-radius:8px;padding:14px 18px;margin-bottom:24px;border:1px solid #e8dcc4;">
        <p style="margin:0 0 3px;font-size:13px;color:#1a1108;">{order.address}</p>
        <p style="margin:0;font-size:13px;color:#1a1108;">{order.city}, {order.state} - {order.pincode}</p>
      </div>

      <!-- Items -->
      <h3 style="margin:0 0 12px;font-size:14px;font-weight:700;color:#1a1108;border-bottom:2px solid #c9a84c;padding-bottom:6px;">Items Ordered</h3>
      <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8dcc4;border-radius:8px;overflow:hidden;margin-bottom:24px;">
        <thead>
          <tr style="background:#fdf8f0;">
            <th style="padding:10px 14px;text-align:left;font-size:11px;color:#8a7060;text-transform:uppercase;letter-spacing:1px;">Product</th>
            <th style="padding:10px 14px;text-align:center;font-size:11px;color:#8a7060;text-transform:uppercase;letter-spacing:1px;">Qty</th>
            <th style="padding:10px 14px;text-align:right;font-size:11px;color:#8a7060;text-transform:uppercase;letter-spacing:1px;">Total</th>
          </tr>
        </thead>
        <tbody>{items_html}</tbody>
        <tfoot>
          <tr style="background:#6b1f2a;">
            <td colspan="2" style="padding:12px 14px;color:#fff;font-weight:700;font-size:13px;">Grand Total</td>
            <td style="padding:12px 14px;color:#e8c97a;font-weight:700;font-size:15px;text-align:right;">&#8377;{order.total_price}</td>
          </tr>
        </tfoot>
      </table>

      <!-- Admin Link -->
      <div style="text-align:center;">
        <a href="http://127.0.0.1:8000/dashboard/orders/{order.id}/" style="display:inline-block;background:#c9a84c;color:#fff;text-decoration:none;padding:12px 28px;border-radius:6px;font-size:13px;font-weight:700;">
          View Order in Dashboard &rarr;
        </a>
      </div>

    </td>
  </tr>

  <!-- FOOTER -->
  <tr>
    <td style="background:#fdf8f0;padding:16px 32px;text-align:center;border-top:1px solid #e8dcc4;">
      <p style="margin:0;font-size:11px;color:#8a7060;">Automated notification from Isha Return Gifts Admin System</p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    text_content = f"""
NEW ORDER - Isha Return Gifts Admin
=====================================
Order ID   : #{order.get_short_order_id()}
Amount     : Rs.{order.total_price}
Payment ID : {order.payment_id}
Status     : {order.payment_status.title()}
Date       : {order.created_at.strftime('%d %b %Y, %I:%M %p')}

CUSTOMER
---------
Name  : {order.customer_name}
Phone : {order.customer_phone}
Email : {order.customer_email or 'Not provided'}

SHIPPING ADDRESS
-----------------
{order.address}
{order.city}, {order.state} - {order.pincode}

ITEMS
------
{items_text}
Total : Rs.{order.total_price}

View Order: http://127.0.0.1:8000/dashboard/orders/{order.id}/
"""

    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[admin_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        print(f"[Email] ✅ Admin notification sent to {admin_email}")
    except Exception as e:
        print(f"[Email] ❌ Failed to send admin email: {e}")
        print("[Email] Tip: Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py")
