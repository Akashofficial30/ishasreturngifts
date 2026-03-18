from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Testimonial


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:8]
    popular_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    categories = Category.objects.all()
    testimonials = Testimonial.objects.filter(is_active=True)[:3]
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'popular_products': popular_products,
        'categories': categories,
        'testimonials': testimonials,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    category_slug = request.GET.get('category', '')
    search = request.GET.get('search', '')
    featured = request.GET.get('featured', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(name__icontains=search)
    if featured:
        products = products.filter(is_featured=True)
    active_category = None
    if category_slug:
        active_category = Category.objects.filter(slug=category_slug).first()
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'search': search,
        'total_count': products.count(),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(id=product.id)[:4]
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


# ── CART — requires login ──────────────────────────────
@login_required(login_url='/users/login/')
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
    """Cart is viewable without login, but checkout requires login"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    return render(request, 'products/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


@login_required(login_url='/users/login/')
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


@login_required(login_url='/users/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')
