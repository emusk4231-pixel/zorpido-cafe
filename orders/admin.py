<<<<<<< HEAD
"""
Admin configuration for order management
"""

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Inline admin for order items
    """
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal', 'item_price']
    fields = ['menu_item', 'item_name', 'item_price', 'quantity', 'subtotal', 'special_instructions']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for orders
    """
    list_display = ['order_number', 'customer', 'order_type', 'status', 
                    'total', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['order_type', 'status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer__username', 'customer__full_name']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 
                       'updated_at', 'completed_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'staff', 'order_type', 'status')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'discount', 'delivery_fee', 'total')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'paid_amount')
        }),
        ('Loyalty Points', {
            'fields': ('loyalty_points_used', 'loyalty_points_earned')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'staff_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """Mark orders as completed"""
        for order in queryset:
            order.mark_as_completed()
        self.message_user(request, f'{queryset.count()} order(s) marked as completed.')
    mark_as_completed.short_description = "Mark as completed"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for order items
    """
    list_display = ['order', 'menu_item', 'quantity', 'item_price', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'item_name']
    readonly_fields = ['subtotal', 'created_at', 'updated_at']
    ordering = ['-created_at']
    actions = ['mark_as_cancelled']

    def mark_as_cancelled(self, request, queryset):
        """Mark order items' related orders as cancelled where applicable"""
        # OrderItem doesn't have a status field in the model; cancelling should update the parent Order(s)
        orders = set(item.order for item in queryset)
        updated = 0
        for order in orders:
            order.status = 'cancelled'
            order.save()
            updated += 1
        self.message_user(request, f'{updated} order(s) marked as cancelled.')
    mark_as_cancelled.short_description = "Mark as cancelled"

=======
"""
Admin configuration for order management
"""

from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    """
    Inline admin for order items
    """
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal', 'item_price']
    fields = ['menu_item', 'item_name', 'item_price', 'quantity', 'subtotal', 'special_instructions']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin interface for orders
    """
    list_display = ['order_number', 'customer', 'order_type', 'status', 
                    'total', 'payment_method', 'payment_status', 'created_at']
    list_filter = ['order_type', 'status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'customer__username', 'customer__full_name']
    readonly_fields = ['order_number', 'subtotal', 'total', 'created_at', 
                       'updated_at', 'completed_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'staff', 'order_type', 'status')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'discount', 'delivery_fee', 'total')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_status', 'paid_amount')
        }),
        ('Loyalty Points', {
            'fields': ('loyalty_points_used', 'loyalty_points_earned')
        }),
        ('Delivery Information', {
            'fields': ('delivery_address',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'staff_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_completed(self, request, queryset):
        """Mark orders as completed"""
        for order in queryset:
            order.mark_as_completed()
        self.message_user(request, f'{queryset.count()} order(s) marked as completed.')
    mark_as_completed.short_description = "Mark as completed"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Admin interface for order items
    """
    list_display = ['order', 'menu_item', 'quantity', 'item_price', 'subtotal', 'created_at']
    list_filter = ['created_at']
    search_fields = ['order__order_number', 'item_name']
    readonly_fields = ['subtotal', 'created_at', 'updated_at']
    ordering = ['-created_at']
    actions = ['mark_as_cancelled']

    def mark_as_cancelled(self, request, queryset):
        """Mark order items' related orders as cancelled where applicable"""
        # OrderItem doesn't have a status field in the model; cancelling should update the parent Order(s)
        orders = set(item.order for item in queryset)
        updated = 0
        for order in orders:
            order.status = 'cancelled'
            order.save()
            updated += 1
        self.message_user(request, f'{updated} order(s) marked as cancelled.')
    mark_as_cancelled.short_description = "Mark as cancelled"

>>>>>>> df6fb379555319efdf513182b2e65dbdd28a0164
    