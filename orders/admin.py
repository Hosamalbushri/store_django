# admin.py
from django.contrib import admin

from customers.models import Address
from .models import Order, OrderItem, PaymentMethod  # Make sure to import your Order and OrderItem models

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
    list_display = ('user', 'order_number','status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email','order_number')
    list_display_links = ('user','order_number')

    
    
    def has_add_permission(self, request, obj=None):
        return False  # Disable the "Add" button

    def has_change_permission(self, request, obj=None):
        return True  # Allow editing of existing items

    def has_delete_permission(self, request, obj=None):
        return False  # Allow deleting existing items (optional)
    
    # fields = (
        
    #     # Add user fields here if needed
       
       
    # )
    
    readonly_fields = (
        'user_username', 
        'user_email',
        'created_at', 
        'updated_at', 
        'Order_number',

        'address_name',
        'address_email', 
        'address_phone_number', 
        'address_street',
        'address_city', 
        'address_postal_code',
        'address_country'
         
       
    ) 
    fieldsets = (
        ('Order Info', {
        'fields': (
        'Order_number',
        'status',
        'created_at', 
        'updated_at',
        )
        }),
         ('Customer Info', {
        'fields': (
        'user_username',
        'user_email',
        
        )
        }),
        ('Order Address', {
        'fields': (
        'address_name', 
        'address_email', 
        'address_postal_code',
        'address_phone_number',
        'address_country',
        'address_city',
        'address_street',),
        }),
       
    )

    inlines = [OrderItemInline]  # Include order items as an inline

    def Order_number(self, obj):
        return obj.order_number
    
    
    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'Username'

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    
        # Address field methods
    def address_name(self, obj):
        return obj.shipping_address.name
    address_name.short_description = 'Recipient Name'

    def address_email(self, obj):
        return obj.shipping_address.email
    address_email.short_description = 'Recipient Email'

    def address_phone_number(self, obj):
        return obj.shipping_address.phone_number
    address_phone_number.short_description = 'Recipient Phone Number'

    def address_street(self, obj):
        return obj.shipping_address.street
    address_street.short_description = 'Street'

    def address_city(self, obj):
        return obj.shipping_address.city
    address_city.short_description = 'City'

    def address_postal_code(self, obj):
        return obj.shipping_address.postal_code
    address_postal_code.short_description = 'Postal Code'

    def address_country(self, obj):
        return obj.shipping_address.country
    address_country.short_description = 'Country'


    
    def save_model(self, request, obj, form, change):
        # Save the updated order status
        super().save_model(request, obj, form, change)

# Register the OrderAdmin with the Order model




class PaymentMethodAdmin(admin.ModelAdmin):
   

    # Allow inline editing if Payment is added as an inline in OrderAdmin
    def has_add_permission(self, request, obj=None):
        return True  # Disables add button if needed
    
admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
