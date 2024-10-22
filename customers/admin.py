from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer ,Address




class AddressInline(admin.TabularInline):  # or admin.StackedInline for a different layout
    model = Address
    extra = 1  # Number of empty address forms to display by default
    fields = ['street_address', 'city', 'state', 'postal_code', 'country']  # Fields to display
    readonly_fields = ['customer']  # You can make the customer field read-only if needed
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing customer
            return ['street_address', 'city', 'state', 'postal_code', 'country']
        return super().get_readonly_fields(request, obj)

class CustomerAdmin(admin.ModelAdmin):
    model = Customer
    list_display = ['email', 'name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['email', 'name']
    ordering = ['email']
      # Disable the 'Add' button in the admin
    def has_add_permission(self, request):
        return False
    
    
    fields = ['name', 'email', 'gender', 'birthday', 'is_active']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:  # Editing an existing customer
            form.base_fields.pop('password', None)  # Remove 'password' field from the form
        return form

    # Allow only the 'active' field to be editable by the admin
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing customer
            return ['name', 'email', 'gender', 'birthday']
        return super().get_readonly_fields(request, obj)
    
    inlines = [AddressInline]

admin.site.register(Customer, CustomerAdmin)
