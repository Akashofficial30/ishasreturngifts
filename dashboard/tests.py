"""Regression tests for the dashboard's Excel product import."""
import io
from decimal import Decimal

import openpyxl
from django.test import TestCase

from dashboard.import_utils import import_products_from_excel
from products.models import Category, Product

HEADERS = ['Name', 'Category', 'Description', 'Price', 'Offer Price', 'Stock', 'Featured', 'Active']


def workbook(rows, headers=HEADERS):
    """An in-memory .xlsx with the given header row and data rows."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)
    return stream


class ImportTests(TestCase):
    def test_a_valid_row_imports(self):
        success, errors = import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', 450, 349, 20, 'Yes', 'Yes'],
        ]))
        self.assertEqual((success, errors), (1, []))
        product = Product.objects.get()
        self.assertEqual(product.name, 'Brass Diya')
        self.assertEqual(product.price, Decimal('450.00'))
        self.assertEqual(product.offer_price, Decimal('349.00'))
        self.assertEqual(product.stock_quantity, 20)
        self.assertTrue(product.is_featured)

    def test_blank_name_does_not_create_a_product_called_none(self):
        """str(row.get('name', '')) yielded 'None' for an empty cell."""
        success, errors = import_products_from_excel(workbook([
            [None, 'Pooja Items', 'No name here', 450, None, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(success, 0)
        self.assertEqual(Product.objects.count(), 0)
        self.assertFalse(Product.objects.filter(name='None').exists())

    def test_blank_category_falls_back_instead_of_creating_none(self):
        import_products_from_excel(workbook([
            ['Brass Diya', None, 'A diya', 450, None, 5, 'No', 'Yes'],
        ]))
        self.assertFalse(Category.objects.filter(name='None').exists())
        self.assertEqual(Product.objects.get().category.name, 'General')

    def test_blank_description_is_not_the_string_none(self):
        import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', None, 450, None, 5, 'No', 'Yes'],
        ]))
        self.assertNotEqual(Product.objects.get().description, 'None')

    def test_negative_price_is_rejected(self):
        success, errors = import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', -450, None, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(success, 0)
        self.assertEqual(Product.objects.count(), 0)
        self.assertTrue(errors)

    def test_offer_price_above_price_is_ignored(self):
        """An offer above list price produced a negative discount badge."""
        success, errors = import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', 450, 900, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(success, 1)
        self.assertIsNone(Product.objects.get().offer_price)
        self.assertTrue(errors)

    def test_price_keeps_decimal_precision(self):
        import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', '₹1,499.99', None, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(Product.objects.get().price, Decimal('1499.99'))

    def test_non_latin_name_still_gets_a_usable_slug(self):
        """slugify() returns '' for Tamil text; an empty slug has no URL."""
        success, _ = import_products_from_excel(workbook([
            ['தமிழ் பரிசு', 'Pooja Items', 'A gift', 450, None, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(success, 1)
        self.assertTrue(Product.objects.get().slug)

    def test_negative_stock_is_clamped(self):
        import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', 450, None, -10, 'No', 'Yes'],
        ]))
        self.assertEqual(Product.objects.get().stock_quantity, 0)

    def test_duplicate_names_get_distinct_slugs(self):
        success, _ = import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', 450, None, 5, 'No', 'Yes'],
            ['Brass Diya', 'Pooja Items', 'Another', 460, None, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(success, 2)
        self.assertEqual(len({p.slug for p in Product.objects.all()}), 2)

    def test_blank_rows_are_skipped_silently(self):
        success, errors = import_products_from_excel(workbook([
            ['Brass Diya', 'Pooja Items', 'A diya', 450, None, 5, 'No', 'Yes'],
            [None, None, None, None, None, None, None, None],
        ]))
        self.assertEqual((success, errors), (1, []))

    def test_missing_required_column_is_reported(self):
        success, errors = import_products_from_excel(
            workbook([['Brass Diya', 'x']], headers=['Name', 'Description'])
        )
        self.assertEqual(success, 0)
        self.assertIn('price', errors[0].lower())

    def test_a_bad_row_does_not_abort_the_whole_import(self):
        success, errors = import_products_from_excel(workbook([
            ['Good One', 'Pooja Items', 'ok', 450, None, 5, 'No', 'Yes'],
            ['Bad One', 'Pooja Items', 'ok', 'not-a-price', None, 5, 'No', 'Yes'],
            ['Good Two', 'Pooja Items', 'ok', 460, None, 5, 'No', 'Yes'],
        ]))
        self.assertEqual(success, 2)
        self.assertEqual(len(errors), 1)
