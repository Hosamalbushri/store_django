# admin.py
from django.contrib import admin

from customers.models import Address
from .models import Order, OrderItem  # Make sure to import your Order and OrderItem models

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0  # Number of empty forms to display
    fields = ('product', 'quantity', 'price', 'product_attributes')

    readonly_fields = ('product', 'quantity', 'price', 'product_attributes')  # Make these fields read-only
    def has_add_permission(self, request, obj=None):
        return False  # Disable the "Add" button

    def has_change_permission(self, request, obj=None):
        return False  # Allow editing of existing items
    def has_delete_permission(self, request, obj=None):
        return False  # Allow deleting existing items (optional)
    
    



class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    
    
    def has_add_permission(self, request, obj=None):
        return False  # Disable the "Add" button

    def has_change_permission(self, request, obj=None):
        return True  # Allow editing of existing items

    def has_delete_permission(self, request, obj=None):
        return False  # Allow deleting existing items (optional)
    
    fields = (
        'user_username',
        'user_email',
        'shipping_address', 
        'status', 
        'created_at', 
        'updated_at',
        # Add user fields here if needed
       
       
    )
    
    readonly_fields = (
        'user_username', 
        'user_email',
        'created_at', 
        'updated_at', 
         
       
    ) 

    inlines = [OrderItemInline]  # Include order items as an inline

    
    
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


    
    def save_model(self, request, obj, form, change):
        # Save the updated order status
        super().save_model(request, obj, form, change)

# Register the OrderAdmin with the Order model
admin.site.register(Order, OrderAdmin)
