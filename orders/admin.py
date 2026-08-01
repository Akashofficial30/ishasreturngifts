from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_price', 'quantity', 'get_subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['get_short_order_id', 'customer_name', 'customer_phone', 'total_price', 'payment_status', 'order_status', 'created_at']
    list_filter = ['payment_status', 'order_status', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'payment_id']
    list_editable = ['order_status']
    readonly_fields = ['order_id', 'payment_id', 'razorpay_order_id', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_id', 'order_status', 'notess')}),
        ('Customer', {'fields': ('customer_name', 'customer_email', 'customer_phone')}),
        ('Shipping', {'fields': ('address', 'city', 'state', 'pincode')}),
        ('Payment', {'fields': ('total_price', 'payment_status', 'payment_id', 'razorpay_order_id')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
