from django.contrib import admin
from .models import Category, Product, ProductImage, Cart, CartItem, Testimonial


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'offer_price', 'stock_quantity', 'is_featured', 'is_active', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active', 'stock_quantity']
    inlines = [ProductImageInline]
    fieldsets = (
        ('Basic Info', {'fields': ('category', 'name', 'slug', 'description')}),
        ('Pricing', {'fields': ('price', 'offer_price')}),
        ('Media', {'fields': ('image',)}),
        ('Inventory', {'fields': ('stock_quantity',)}),
        ('Settings', {'fields': ('is_featured', 'is_active')}),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_active', 'created_at']
    list_editable = ['is_active']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'get_item_count', 'get_total', 'created_at']
    inlines = [CartItemInline]
