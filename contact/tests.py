"""Tests for the contact form and its notification emails."""
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from contact.models import ContactMessage

FORM = {
    'name': 'Priya',
    'email': 'priya@example.com',
    'phone': '9876543210',
    'subject': 'bulk',
    'message': 'Do you do 200 pieces for a wedding?',
}


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ADMIN_EMAIL='shop@example.com',
    DEFAULT_FROM_EMAIL='noreply@example.com',
)
class ContactEmailTests(TestCase):
    def post(self, **overrides):
        return self.client.post(reverse('contact'), dict(FORM, **overrides))

    def test_submission_sends_both_emails(self):
        self.post()
        self.assertEqual(len(mail.outbox), 2)
        recipients = {m.to[0] for m in mail.outbox}
        self.assertEqual(recipients, {'shop@example.com', 'priya@example.com'})

    def test_admin_alert_carries_the_enquiry(self):
        self.post()
        admin = next(m for m in mail.outbox if m.to == ['shop@example.com'])
        self.assertIn('Priya', admin.subject)
        self.assertIn('Bulk Order Enquiry', admin.subject)
        self.assertIn('Do you do 200 pieces', admin.body)
        self.assertIn('9876543210', admin.body)

    def test_admin_alert_replies_to_the_customer(self):
        """Hitting Reply in the shop inbox should reach the customer."""
        self.post()
        admin = next(m for m in mail.outbox if m.to == ['shop@example.com'])
        self.assertEqual(admin.reply_to, ['priya@example.com'])

    def test_customer_gets_an_acknowledgement(self):
        self.post()
        ack = next(m for m in mail.outbox if m.to == ['priya@example.com'])
        self.assertIn('received your message', ack.subject.lower())
        self.assertIn('Priya', ack.body)

    def test_both_emails_have_html_and_plain_text(self):
        self.post()
        for message in mail.outbox:
            self.assertTrue(message.body.strip(), 'plain text body missing')
            self.assertEqual(len(message.alternatives), 1)
            self.assertEqual(message.alternatives[0][1], 'text/html')

    def test_message_is_saved(self):
        self.post()
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.name, 'Priya')
        self.assertEqual(saved.status, 'new')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    ADMIN_EMAIL='shop@example.com',
)
class ContactValidationTests(TestCase):
    def post(self, **overrides):
        return self.client.post(reverse('contact'), dict(FORM, **overrides))

    def test_blank_submission_is_rejected(self):
        self.client.post(reverse('contact'), {})
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_is_rejected(self):
        self.post(email='not-an-email')
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_empty_message_is_rejected(self):
        self.post(message='   ')
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_unknown_subject_falls_back_to_other(self):
        self.post(subject='../../etc/passwd')
        self.assertEqual(ContactMessage.objects.get().subject, 'other')

    def test_phone_is_optional(self):
        self.post(phone='')
        self.assertEqual(ContactMessage.objects.count(), 1)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class ContactWithoutAdminEmailTests(TestCase):
    @override_settings(ADMIN_EMAIL='')
    def test_unconfigured_admin_email_still_acknowledges_the_customer(self):
        self.client.post(reverse('contact'), FORM)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual([m.to[0] for m in mail.outbox], ['priya@example.com'])

    @override_settings(ADMIN_EMAIL='your_gmail@gmail.com')
    def test_placeholder_admin_email_is_not_mailed(self):
        self.client.post(reverse('contact'), FORM)
        self.assertNotIn('your_gmail@gmail.com', [m.to[0] for m in mail.outbox])


class ContactMailFailureTests(TestCase):
    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend',
        EMAIL_HOST='127.0.0.1',
        EMAIL_PORT=1,          # nothing is listening: connection refused
        EMAIL_TIMEOUT=1,
        ADMIN_EMAIL='shop@example.com',
    )
    def test_the_enquiry_survives_a_mail_server_failure(self):
        """A dead SMTP server must not lose the customer's message."""
        response = self.client.post(reverse('contact'), FORM)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
