from django.contrib import admin
from django.utils.html import mark_safe
from customers.models import Address, Customer
    
class CustomerAdmin(admin.ModelAdmin):
    list_display = ( 'phone_number', 'user_email', 'phone_number', 'is_active')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('user_email', 'user_first_name', 'user_last_name','gender','phone_number','birthday','address_list')  # Adding related fields as readonly
    
    def has_delete_permission(self, request, obj=None):
        # Disallow delete permission for all users
        return False
    
    def has_add_permission(self, request):
        # Disallow adding new Address entries in the admin
        return False
    

    def address_list(self, obj):
        addresses = Address.objects.filter(user=obj.user)
        
        if not addresses:
            return "No addresses available"
        
        # Format the addresses as HTML
        address_html = "<br>".join(
            [
                f"<p><strong>Name:</strong> {address.name}<br>"
                f"<strong>Email:</strong> {address.email}<br>"
                f"<strong>Phone:</strong> {address.phone_number}<br>"
                f"<strong>Country:</strong> {address.country}<br>"
                f"<strong>City:</strong> {address.city}<br>"
                f"<strong>Street:</strong> {address.street}<br>"
                f"<strong>Postal Code:</strong> {address.postal_code}<br><hr></p>"
                for address in addresses
            ]
        )
        return mark_safe(address_html)  # Use mark_safe to render as HTML in the admin
    address_list.short_description = "Addresses"


    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'

    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'First Name'

    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Last Name'
    
    # Add the user fields to fieldsets if needed
    fieldsets = (
        (None, {
            'fields': ('user_email', 'user_first_name', 'user_last_name', 'phone_number', 'gender', 'birthday')
        }),
        ('Customer Status', {
            'fields': ['is_active'],
        }),
        ('Addresses', {   # Separate fieldset for addresses
            'fields': ('address_list',),
        }),
    )
    

    
    

admin.site.register(Customer, CustomerAdmin)
