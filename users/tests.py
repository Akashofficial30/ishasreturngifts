"""Regression tests for authentication."""
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LoginRedirectTests(TestCase):
    def setUp(self):
        User.objects.create_user('alice', password='Sup3rSecret!pw')

    def test_next_cannot_send_you_off_site(self):
        """?next= was passed straight to redirect() — an open redirect."""
        response = self.client.post(
            reverse('login') + '?next=https://evil.example.com/phish',
            {'username': 'alice', 'password': 'Sup3rSecret!pw'},
        )
        self.assertNotIn('evil.example.com', response['Location'])

    def test_next_still_works_for_internal_paths(self):
        response = self.client.post(
            reverse('login') + '?next=/cart/',
            {'username': 'alice', 'password': 'Sup3rSecret!pw'},
        )
        self.assertEqual(response['Location'], '/cart/')

    def test_bad_password_does_not_log_you_in(self):
        response = self.client.post(
            reverse('login'), {'username': 'alice', 'password': 'wrong'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)


class RegistrationTests(TestCase):
    def test_weak_passwords_are_rejected(self):
        """AUTH_PASSWORD_VALIDATORS were configured but never invoked."""
        self.client.post(reverse('register'), {
            'username': 'bob', 'email': 'bob@example.com',
            'password1': '123', 'password2': '123',
        })
        self.assertFalse(User.objects.filter(username='bob').exists())

    def test_mismatched_passwords_are_rejected(self):
        self.client.post(reverse('register'), {
            'username': 'bob', 'email': 'bob@example.com',
            'password1': 'Sup3rSecret!pw', 'password2': 'Different!pw9',
        })
        self.assertFalse(User.objects.filter(username='bob').exists())

    def test_invalid_email_is_rejected(self):
        self.client.post(reverse('register'), {
            'username': 'bob', 'email': 'not-an-email',
            'password1': 'Sup3rSecret!pw', 'password2': 'Sup3rSecret!pw',
        })
        self.assertFalse(User.objects.filter(username='bob').exists())

    def test_duplicate_username_is_rejected_case_insensitively(self):
        User.objects.create_user('bob', password='Sup3rSecret!pw')
        self.client.post(reverse('register'), {
            'username': 'BOB', 'email': 'bob2@example.com',
            'password1': 'An0ther!Passw0rd', 'password2': 'An0ther!Passw0rd',
        })
        self.assertEqual(User.objects.filter(username__iexact='bob').count(), 1)

    def test_a_valid_registration_succeeds_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'bob', 'email': 'bob@example.com',
            'password1': 'Sup3rSecret!pw', 'password2': 'Sup3rSecret!pw',
        })
        self.assertTrue(User.objects.filter(username='bob').exists())
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 302)


class DashboardAccessTests(TestCase):
    def setUp(self):
        User.objects.create_user('alice', password='Sup3rSecret!pw')

    def test_customer_cannot_reach_the_dashboard(self):
        self.client.login(username='alice', password='Sup3rSecret!pw')
        response = self.client.get(reverse('dashboard_home'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/login/', response['Location'])

    def test_anonymous_cannot_export_customer_data(self):
        response = self.client.get(reverse('export_customers_excel'))
        self.assertEqual(response.status_code, 302)
