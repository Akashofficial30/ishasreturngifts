"""Email for contact-form enquiries.

Two messages per submission: an alert to the shop and an acknowledgement to
the customer. Both are best-effort — a mail failure must never lose the
enquiry, which is already saved before these are called.
"""
import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

# The value shipped in .env.example. Treat it as "not configured" so a fresh
# checkout doesn't try to mail a placeholder address.
PLACEHOLDER_EMAIL = 'your_gmail@gmail.com'


def _shop_email():
    admin_email = getattr(settings, 'ADMIN_EMAIL', '')
    if not admin_email or admin_email == PLACEHOLDER_EMAIL:
        return None
    return admin_email


def _send(subject, text_content, html_content, to, reply_to=None):
    """Send one mail, swallowing failures after logging them."""
    if not to:
        return False
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to],
            reply_to=[reply_to] if reply_to else None,
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()
        logger.info('Contact email sent to %s', to)
        return True
    except Exception:
        logger.exception('Failed to send contact email to %s', to)
        return False


def send_contact_admin_notification(message):
    """Alert the shop that a new enquiry has arrived."""
    admin_email = _shop_email()
    if not admin_email:
        logger.info('ADMIN_EMAIL not configured — skipping contact alert.')
        return False

    subject = f'New enquiry: {message.get_subject_display()} from {message.name}'
    phone = message.phone or '—'

    text_content = f"""NEW ENQUIRY - Isha Return Gifts

From    : {message.name}
Email   : {message.email}
Phone   : {phone}
Subject : {message.get_subject_display()}
Received: {message.created_at:%d %b %Y, %I:%M %p}

MESSAGE
-------
{message.message}

Reply directly to this email to respond to {message.name}.
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f5f5f5;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="padding:28px 16px;">
<tr><td align="center">
<table width="580" cellpadding="0" cellspacing="0" style="max-width:580px;width:100%;background:#fff;border-radius:12px;overflow:hidden;border:1px solid #e0d4b8;">

  <tr>
    <td style="background:#1a1108;padding:24px 32px;text-align:center;">
      <h2 style="margin:0;color:#c9a84c;font-weight:400;font-size:20px;">&#10022; Isha Return Gifts — Admin Alert</h2>
      <p style="margin:6px 0 0;color:rgba(255,255,255,0.5);font-size:12px;">New Customer Enquiry</p>
    </td>
  </tr>

  <tr>
    <td style="background:#fff8e6;padding:16px 32px;text-align:center;border-bottom:1px solid #e8dcc4;">
      <p style="margin:0;font-size:16px;color:#8a6020;">
        &#128231; <strong>{message.get_subject_display()}</strong> from <strong>{message.name}</strong>
      </p>
    </td>
  </tr>

  <tr>
    <td style="padding:24px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0" style="font-size:14px;color:#4a3820;">
        <tr><td style="padding:6px 0;width:90px;color:#8a7a60;">Name</td><td style="padding:6px 0;font-weight:700;">{message.name}</td></tr>
        <tr><td style="padding:6px 0;color:#8a7a60;">Email</td><td style="padding:6px 0;"><a href="mailto:{message.email}" style="color:#6b1f2a;">{message.email}</a></td></tr>
        <tr><td style="padding:6px 0;color:#8a7a60;">Phone</td><td style="padding:6px 0;">{phone}</td></tr>
        <tr><td style="padding:6px 0;color:#8a7a60;">Received</td><td style="padding:6px 0;">{message.created_at:%d %b %Y, %I:%M %p}</td></tr>
      </table>
    </td>
  </tr>

  <tr>
    <td style="padding:0 32px 24px;">
      <p style="margin:0 0 8px;font-size:12px;letter-spacing:1px;text-transform:uppercase;color:#8a7a60;">Message</p>
      <div style="background:#fdf8f0;border-left:3px solid #6b1f2a;border-radius:0 8px 8px 0;padding:16px 18px;font-size:14px;line-height:1.7;color:#4a3820;white-space:pre-wrap;">{message.message}</div>
    </td>
  </tr>

  <tr>
    <td style="background:#fdf8f0;padding:18px 32px;text-align:center;border-top:1px solid #e8dcc4;">
      <p style="margin:0;font-size:13px;color:#8a7a60;">Reply to this email to respond to {message.name} directly.</p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    # reply_to the customer, so hitting Reply in the inbox reaches them and not
    # the shop's own from-address.
    return _send(subject, text_content, html_content, admin_email, reply_to=message.email)


def send_contact_acknowledgement(message):
    """Tell the customer their enquiry arrived."""
    subject = 'We received your message | Isha Return Gifts'
    reply_to = _shop_email()

    text_content = f"""Hi {message.name},

Thank you for getting in touch with Isha Return Gifts.

We have received your enquiry about "{message.get_subject_display()}"
and will get back to you within 24 hours.

YOUR MESSAGE
------------
{message.message}

Warm regards,
Isha Return Gifts
"""

    html_content = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#fdf8f0;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#fdf8f0;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

  <tr>
    <td style="background:linear-gradient(135deg,#6b1f2a,#3d0e18);border-radius:12px 12px 0 0;padding:36px 40px;text-align:center;">
      <p style="margin:0 0 6px;font-size:11px;letter-spacing:4px;text-transform:uppercase;color:rgba(255,255,255,0.55);">Premium Return Gifts</p>
      <h1 style="margin:0;font-size:26px;font-weight:400;color:#fff;letter-spacing:1px;">&#10022; Isha Return Gifts</h1>
    </td>
  </tr>

  <tr>
    <td style="background:#fff;padding:36px 40px;">
      <p style="margin:0 0 16px;font-size:17px;color:#3d2b18;">Hi <strong>{message.name}</strong>,</p>
      <p style="margin:0 0 20px;font-size:15px;line-height:1.7;color:#4a3820;">
        Thank you for getting in touch. We have received your enquiry about
        <strong>{message.get_subject_display()}</strong> and will get back to you
        within 24 hours.
      </p>

      <p style="margin:0 0 8px;font-size:12px;letter-spacing:1px;text-transform:uppercase;color:#8a7a60;">Your message</p>
      <div style="background:#fdf8f0;border-left:3px solid #c9a84c;border-radius:0 8px 8px 0;padding:16px 18px;font-size:14px;line-height:1.7;color:#4a3820;white-space:pre-wrap;">{message.message}</div>
    </td>
  </tr>

  <tr>
    <td style="background:#1a1108;border-radius:0 0 12px 12px;padding:24px 40px;text-align:center;">
      <p style="margin:0 0 4px;font-size:14px;color:#c9a84c;">Isha Return Gifts</p>
      <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.45);">Premium return gifts, delivered across India.</p>
    </td>
  </tr>

</table>
</td></tr>
</table>
</body>
</html>"""

    return _send(subject, text_content, html_content, message.email, reply_to=reply_to)
