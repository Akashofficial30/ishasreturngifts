from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Product, Category, Cart, CartItem, Testimonial


MAX_QUANTITY = 99


def get_or_create_cart(request):
    if not request.session.session_key:
        request.session.create()
    # first()-or-create rather than get_or_create: session_key has no unique
    # constraint, so a race could leave two carts and get_or_create would then
    # raise MultipleObjectsReturned on every later request.
    cart = Cart.objects.filter(session_key=request.session.session_key).first()
    if cart is None:
        cart = Cart.objects.create(session_key=request.session.session_key)
    return cart


def get_cart(request):
    """The session's cart, without creating one. None if there isn't one."""
    if not request.session.session_key:
        return None
    return Cart.objects.filter(session_key=request.session.session_key).first()


def parse_quantity(raw, default=1):
    """Clamp a user-supplied quantity to a sane range.

    Anything non-numeric previously reached int() directly and returned a 500.
    """
    try:
        quantity = int(raw)
    except (TypeError, ValueError):
        return default
    return max(0, min(quantity, MAX_QUANTITY))


def home(request):
    # select_related('category') — the product card renders product.category.name.
    featured_products = Product.objects.filter(
        is_featured=True, is_active=True
    ).select_related('category')[:8]
    popular_products = Product.objects.filter(
        is_active=True
    ).select_related('category').order_by('-created_at')[:8]
    # annotate — the category card renders a per-category product count.
    categories = Category.objects.annotate(product_count=Count('products'))
    testimonials = Testimonial.objects.filter(is_active=True)[:3]
    return render(request, 'home.html', {
        'featured_products': featured_products,
        'popular_products': popular_products,
        'categories': categories,
        'testimonials': testimonials,
    })


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.annotate(product_count=Count('products'))
    category_slug = request.GET.get('category', '')
    search = request.GET.get('search', '')
    featured = request.GET.get('featured', '')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search:
        products = products.filter(name__icontains=search)
    if featured:
        products = products.filter(is_featured=True)
    # Evaluate both querysets once: the template iterates them, so a separate
    # .count() and a separate lookup for the active category are wasted queries.
    categories = list(categories)
    products = list(products)
    active_category = None
    if category_slug:
        active_category = next((c for c in categories if c.slug == category_slug), None)
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        # The template reads selected_category/search_query; the old names
        # never matched, so the active filter and the search box were dead.
        'active_category': active_category,
        'selected_category': category_slug,
        'search': search,
        'search_query': search,
        'total_count': len(products),
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
    quantity = parse_quantity(request.POST.get('quantity'))
    if quantity < 1:
        return redirect('product_detail', slug=product.slug)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    new_quantity = quantity if created else cart_item.quantity + quantity
    cart_item.quantity = min(new_quantity, MAX_QUANTITY)
    cart_item.save()
    messages.success(request, f'"{product.name}" added to cart!')
    # Only follow the referer when it points back into this site.
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect('product_list')


def cart(request):
    """Cart is viewable without login, but checkout requires login."""
    # Don't create a cart just because someone looked at the page — that wrote
    # a row (and a session) for every visitor who clicked the bag icon.
    cart = get_cart(request)
    cart_items = cart.items.select_related('product').all() if cart else []
    return render(request, 'products/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })


@login_required(login_url='/users/login/')
def update_cart(request, item_id):
    # Scope the lookup to this session's cart — an unscoped lookup let any
    # logged-in user edit another shopper's cart by guessing the item id.
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__session_key=request.session.session_key
    )
    quantity = parse_quantity(request.POST.get('quantity'))
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


@login_required(login_url='/users/login/')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__session_key=request.session.session_key
    )
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')
