"""Regression tests for the catalogue and cart."""
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Cart, CartItem, Category, Product


class CartTestCase(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Home Decor', slug='home-decor')
        self.product = Product.objects.create(
            category=self.category, name='Wall Art', slug='wall-art',
            description='Art', price=Decimal('250.00'), stock_quantity=10,
        )
        User.objects.create_user('alice', password='Sup3rSecret!pw')
        User.objects.create_user('mallory', password='Sup3rSecret!pw')

    def login(self, user='alice'):
        self.client.login(username=user, password='Sup3rSecret!pw')


class QuantityParsingTests(CartTestCase):
    def test_non_numeric_quantity_does_not_crash(self):
        """int(request.POST['quantity']) raised ValueError -> 500."""
        self.login()
        response = self.client.post(
            reverse('add_to_cart', args=[self.product.id]), {'quantity': 'abc'}
        )
        self.assertIn(response.status_code, (301, 302))
        self.assertEqual(CartItem.objects.get().quantity, 1)

    def test_negative_quantity_does_not_create_an_item(self):
        self.login()
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]), {'quantity': '-5'}
        )
        self.assertEqual(CartItem.objects.count(), 0)

    def test_quantity_is_capped(self):
        self.login()
        self.client.post(
            reverse('add_to_cart', args=[self.product.id]), {'quantity': '100000'}
        )
        self.assertEqual(CartItem.objects.get().quantity, 99)


class CartOwnershipTests(CartTestCase):
    def alice_cart_item(self):
        self.login('alice')
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        item = CartItem.objects.get()
        self.client.logout()
        return item

    def test_a_stranger_cannot_change_your_cart(self):
        """The lookup was by item id alone, with no owner check."""
        item = self.alice_cart_item()
        self.login('mallory')
        response = self.client.post(
            reverse('update_cart', args=[item.id]), {'quantity': 99}
        )
        self.assertEqual(response.status_code, 404)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_a_stranger_cannot_delete_your_cart_item(self):
        item = self.alice_cart_item()
        self.login('mallory')
        response = self.client.post(reverse('remove_from_cart', args=[item.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(id=item.id).exists())


class CartPageTests(CartTestCase):
    def test_viewing_the_cart_does_not_create_a_cart_row(self):
        self.client.get(reverse('cart'))
        self.assertEqual(Cart.objects.count(), 0)

    def test_cart_totals(self):
        self.login()
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 3})
        cart = Cart.objects.get()
        self.assertEqual(cart.get_item_count(), 3)
        self.assertEqual(cart.get_total(), Decimal('750.00'))

    def test_offer_price_wins_over_list_price(self):
        self.product.offer_price = Decimal('200.00')
        self.product.save()
        self.login()
        self.client.post(reverse('add_to_cart', args=[self.product.id]), {'quantity': 2})
        self.assertEqual(Cart.objects.get().get_total(), Decimal('400.00'))


class CatalogueTests(CartTestCase):
    def test_inactive_products_are_hidden(self):
        Product.objects.create(
            category=self.category, name='Hidden', slug='hidden',
            description='x', price=Decimal('10.00'), is_active=False,
        )
        response = self.client.get(reverse('product_list'))
        self.assertNotContains(response, 'Hidden')

    def test_inactive_product_detail_is_404(self):
        self.product.is_active = False
        self.product.save()
        response = self.client.get(reverse('product_detail', args=[self.product.slug]))
        self.assertEqual(response.status_code, 404)

    def test_category_filter(self):
        other = Category.objects.create(name='Kitchen', slug='kitchen')
        Product.objects.create(
            category=other, name='Steel Tumbler', slug='steel-tumbler',
            description='x', price=Decimal('50.00'),
        )
        response = self.client.get(reverse('product_list'), {'category': 'kitchen'})
        self.assertContains(response, 'Steel Tumbler')
        self.assertNotContains(response, 'Wall Art')
