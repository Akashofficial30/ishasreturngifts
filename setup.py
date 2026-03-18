#!/usr/bin/env python
"""
Isha Return Gifts – One-time Setup Script
Run: python setup.py
This will:
  1. Apply migrations
  2. Create superuser (admin / admin@12345)
  3. Seed sample categories, products, testimonials
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'isha_return_gifts.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils.text import slugify
from products.models import Category, Product, Testimonial


def create_superuser():
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@ishareturnGifts.com', 'admin@12345')
        print("✅ Superuser created: admin / admin@12345")
    else:
        print("ℹ️  Superuser 'admin' already exists.")


def create_categories():
    categories_data = [
        {'name': 'Wedding Return Gifts', 'description': 'Elegant gifts for wedding guests'},
        {'name': 'Pooja Items', 'description': 'Sacred items for religious ceremonies'},
        {'name': 'Home Décor', 'description': 'Beautiful home decoration pieces'},
        {'name': 'Kitchen Essentials', 'description': 'Useful kitchen items as gifts'},
        {'name': 'Baby Shower Gifts', 'description': 'Cute gifts for baby shower celebrations'},
        {'name': 'Customized Gifts', 'description': 'Personalized gifts for every occasion'},
    ]
    categories = {}
    for data in categories_data:
        slug = slugify(data['name'])
        cat, created = Category.objects.get_or_create(slug=slug, defaults={
            'name': data['name'],
            'description': data['description'],
        })
        categories[data['name']] = cat
        status = "✅ Created" if created else "ℹ️  Exists"
        print(f"{status}: Category '{data['name']}'")
    return categories


def create_products(categories):
    products_data = [
        {
            'name': 'Brass Deepam Set',
            'category': 'Pooja Items',
            'description': 'Traditional brass deepam set perfect for pooja ceremonies. Hand-crafted with intricate designs. Ideal as a return gift for weddings and religious events.',
            'price': 450.00,
            'offer_price': 349.00,
            'stock_quantity': 200,
            'is_featured': True,
        },
        {
            'name': 'Sandalwood Soap Gift Box',
            'category': 'Wedding Return Gifts',
            'description': 'Premium sandalwood soap set beautifully packaged in a gift box. Made with natural ingredients and a soothing fragrance.',
            'price': 299.00,
            'offer_price': 249.00,
            'stock_quantity': 500,
            'is_featured': True,
        },
        {
            'name': 'Copper Water Bottle',
            'category': 'Kitchen Essentials',
            'description': 'Pure copper water bottle with Ayurvedic benefits. Keeps water cool and healthy. Great for weddings and housewarming gifting.',
            'price': 599.00,
            'offer_price': 499.00,
            'stock_quantity': 150,
            'is_featured': True,
        },
        {
            'name': 'Miniature Ganesha Idol',
            'category': 'Home Décor',
            'description': 'Beautifully crafted miniature Ganesha idol in white marble finish. A symbol of prosperity and good luck for every home.',
            'price': 350.00,
            'offer_price': None,
            'stock_quantity': 300,
            'is_featured': True,
        },
        {
            'name': 'Silk Pouch with Dry Fruits',
            'category': 'Wedding Return Gifts',
            'description': 'Elegant silk pouch filled with premium dry fruits – almonds, cashews, and raisins. Perfect for weddings and festivals.',
            'price': 399.00,
            'offer_price': 329.00,
            'stock_quantity': 400,
            'is_featured': True,
        },
        {
            'name': 'Agarbatti Gift Set',
            'category': 'Pooja Items',
            'description': 'Premium agarbatti (incense sticks) gift set with 5 divine fragrances: Rose, Jasmine, Sandalwood, Mogra, and Lavender.',
            'price': 199.00,
            'offer_price': 149.00,
            'stock_quantity': 600,
            'is_featured': False,
        },
        {
            'name': 'Handloom Cotton Towel Set',
            'category': 'Wedding Return Gifts',
            'description': 'Set of 2 premium handloom cotton towels with traditional border design. Soft, absorbent and durable – perfect for gifting.',
            'price': 499.00,
            'offer_price': 399.00,
            'stock_quantity': 250,
            'is_featured': False,
        },
        {
            'name': 'Terracotta Clay Pot',
            'category': 'Home Décor',
            'description': 'Authentic hand-painted terracotta clay pot. Eco-friendly and artistic. Great for home décor and as return gift.',
            'price': 280.00,
            'offer_price': None,
            'stock_quantity': 180,
            'is_featured': False,
        },
        {
            'name': 'Baby Elephant Money Bank',
            'category': 'Baby Shower Gifts',
            'description': 'Adorable ceramic baby elephant money bank in pastel colors. Perfect baby shower return gift that kids will love.',
            'price': 320.00,
            'offer_price': 269.00,
            'stock_quantity': 220,
            'is_featured': True,
        },
        {
            'name': 'Customized Name Keychain',
            'category': 'Customized Gifts',
            'description': 'Personalized wooden keychain with custom name engraving. Add a special touch to your celebration with personalized gifts.',
            'price': 150.00,
            'offer_price': 99.00,
            'stock_quantity': 1000,
            'is_featured': False,
        },
        {
            'name': 'Steel Tumbler Set (2 pcs)',
            'category': 'Kitchen Essentials',
            'description': 'High-quality stainless steel tumbler set of 2 pieces. Traditional design with modern finish – perfect for South Indian weddings.',
            'price': 350.00,
            'offer_price': 299.00,
            'stock_quantity': 350,
            'is_featured': False,
        },
        {
            'name': 'Scented Candle Gift Box',
            'category': 'Home Décor',
            'description': 'Luxury scented candle set in a premium gift box. Fragrances include Jasmine, Rose, and Vanilla. Long-lasting 40-hour burn time.',
            'price': 550.00,
            'offer_price': 449.00,
            'stock_quantity': 180,
            'is_featured': True,
        },
    ]

    for data in products_data:
        cat_name = data.pop('category')
        category = categories.get(cat_name)
        if not category:
            continue
        slug = slugify(data['name'])
        # Make slug unique
        base_slug = slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults={**data, 'category': category, 'slug': slug}
        )
        status = "✅ Created" if created else "ℹ️  Exists"
        print(f"{status}: Product '{data['name']}'")


def create_testimonials():
    testimonials_data = [
        {
            'name': 'Priya Ramasamy',
            'message': 'Ordered 200 brass deepam sets for our daughter\'s wedding. The quality was exceptional and delivery was on time. Our guests loved it!',
            'rating': 5,
        },
        {
            'name': 'Anand Krishnamurthy',
            'message': 'Isha Return Gifts made our housewarming special. The copper bottles were beautifully packaged and everyone appreciated the thoughtful gifting.',
            'rating': 5,
        },
        {
            'name': 'Meena Subramaniam',
            'message': 'Excellent service! The silk pouches with dry fruits were a huge hit at our baby shower. Will definitely order again for future events.',
            'rating': 5,
        },
        {
            'name': 'Vijay Natarajan',
            'message': 'The customized keychains for our engagement ceremony were perfect. Quick delivery and very responsive customer service.',
            'rating': 4,
        },
        {
            'name': 'Lakshmi Venkatesh',
            'message': 'Quality products at affordable prices. The Ganesha idols were beautifully crafted and made for memorable return gifts.',
            'rating': 5,
        },
        {
            'name': 'Karthik Sundaram',
            'message': 'Ordered bulk for our son\'s wedding reception. Everything was packed beautifully and delivered 2 days early. Highly recommended!',
            'rating': 5,
        },
    ]
    for data in testimonials_data:
        t, created = Testimonial.objects.get_or_create(name=data['name'], defaults=data)
        status = "✅ Created" if created else "ℹ️  Exists"
        print(f"{status}: Testimonial by '{data['name']}'")


if __name__ == '__main__':
    print("\n🎁 Setting up Isha Return Gifts...\n")

    print("👤 Creating admin user...")
    create_superuser()

    print("\n📂 Creating categories...")
    categories = create_categories()

    print("\n🛍️  Creating sample products...")
    create_products(categories)

    print("\n💬 Creating testimonials...")
    create_testimonials()

    print("\n✨ Setup complete! Run: python manage.py runserver")
    print("   Admin panel: http://127.0.0.1:8000/admin/")
    print("   Login: admin / admin@12345\n")
