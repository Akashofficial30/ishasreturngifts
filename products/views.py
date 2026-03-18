from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category, Cart, CartItem, Testimonial


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    popular_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.all()[:6]
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    context = {
        'featured_products': featured_products,
        'popular_products': popular_products,
        'categories': categories,
        'testimonials': testimonials,
    }
    return render(request, 'home.html', context)


def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    else:
        category = None

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))


def cart(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'products/cart.html', context)


def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated.')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')
