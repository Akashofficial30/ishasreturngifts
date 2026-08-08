"""Regression tests for the checkout path.

Each test here pins a defect that was live in the codebase; they are named for
the behaviour they protect rather than the bug number.
"""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from products.models import Category, Product


class CheckoutTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Pooja Items', slug='pooja-items')
        self.product = Product.objects.create(
            category=self.category, name='Brass Diya', slug='brass-diya',
            description='A diya', price=Decimal('100.00'), stock_quantity=5,
        )
        self.alice = User.objects.create_user('alice', password='Sup3rSecret!pw')
        self.mallory = User.objects.create_user('mallory', password='Sup3rSecret!pw')

    def login(self, user='alice'):
        self.client.login(username=user, password='Sup3rSecret!pw')

    def add_to_cart(self, quantity=1):
        return self.client.post(
            reverse('add_to_cart', args=[self.product.id]), {'quantity': quantity}
        )

    def checkout_form(self, **overrides):
        form = {
            'name': 'Alice', 'email': 'alice@example.com', 'phone': '9999999999',
            'address': '1 Test Street', 'city': 'Chennai', 'state': 'Tamil Nadu',
            'pincode': '600001', 'payment_method': 'cod',
        }
        form.update(overrides)
        return form


class CodOrderTests(CheckoutTestCase):
    def test_cod_order_skips_the_payment_gateway(self):
        """COD used to fall through to initiate_payment and 500."""
        self.login()
        self.add_to_cart()
        response = self.client.post(reverse('place_order'), self.checkout_form())
        order = Order.objects.get()
        self.assertRedirects(
            response, reverse('order_confirmation', args=[order.id]),
            fetch_redirect_response=False,
        )
        self.assertEqual(order.order_status, 'confirmed')

    def test_order_is_linked_to_the_user_who_placed_it(self):
        self.login()
        self.add_to_cart()
        self.client.post(reverse('place_order'), self.checkout_form())
        self.assertEqual(Order.objects.get().user, self.alice)


class OrderAccessTests(CheckoutTestCase):
    def place_order_as_alice(self):
        self.login('alice')
        self.add_to_cart()
        self.client.post(reverse('place_order'), self.checkout_form())
        self.client.logout()
        return Order.objects.get()

    def test_another_customer_cannot_read_someone_elses_order(self):
        """The IDOR: sequential ids exposed every customer's address."""
        order = self.place_order_as_alice()
        self.login('mallory')
        response = self.client.get(reverse('order_confirmation', args=[order.id]))
        self.assertEqual(response.status_code, 404)

    def test_owner_can_read_their_own_order(self):
        order = self.place_order_as_alice()
        self.login('alice')
        response = self.client.get(reverse('order_confirmation', args=[order.id]))
        self.assertEqual(response.status_code, 200)

    def test_staff_can_read_any_order(self):
        order = self.place_order_as_alice()
        User.objects.create_user('admin', password='Sup3rSecret!pw', is_staff=True)
        self.client.login(username='admin', password='Sup3rSecret!pw')
        response = self.client.get(reverse('order_confirmation', args=[order.id]))
        self.assertEqual(response.status_code, 200)

    def test_payment_page_rejects_a_stranger(self):
        """initiate_payment had no login requirement and no ownership check."""
        order = self.place_order_as_alice()
        self.login('mallory')
        response = self.client.get(reverse('initiate_payment', args=[order.id]))
        self.assertEqual(response.status_code, 404)


class ValidationTests(CheckoutTestCase):
    def test_missing_address_is_rejected_without_creating_an_order(self):
        """Blank required fields used to hit the NOT NULL constraint."""
        self.login()
        self.add_to_cart()
        response = self.client.post(
            reverse('place_order'), self.checkout_form(address='', city='')
        )
        self.assertRedirects(response, reverse('checkout'), fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 0)

    def test_total_is_computed_server_side(self):
        self.login()
        self.add_to_cart(quantity=2)
        self.client.post(reverse('place_order'), self.checkout_form(total_price='1'))
        self.assertEqual(Order.objects.get().total_price, Decimal('200.00'))


class StockTests(CheckoutTestCase):
    def test_stock_is_decremented_when_an_order_is_placed(self):
        self.login()
        self.add_to_cart(quantity=2)
        self.client.post(reverse('place_order'), self.checkout_form())
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 3)

    def test_ordering_more_than_stock_is_refused(self):
        """Nothing checked stock, so the shop happily oversold."""
        self.product.stock_quantity = 1
        self.product.save()
        self.login()
        self.add_to_cart(quantity=3)
        response = self.client.post(reverse('place_order'), self.checkout_form())
        self.assertRedirects(response, reverse('cart'), fetch_redirect_response=False)
        self.assertEqual(Order.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 1)
