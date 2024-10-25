from django.contrib import admin

from customers.models import Customer




# class AddressInline(admin.TabularInline):  # or admin.StackedInline for a different layout
#     model = Address
#     extra = 1  # Number of empty address forms to display by default
#     fields = ['street_address', 'city', 'state', 'postal_code', 'country']  # Fields to display
#     readonly_fields = ['customer']  # You can make the customer field read-only if needed
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # Editing an existing customer
#             return ['street_address', 'city', 'state', 'postal_code', 'country']
#         return super().get_readonly_fields(request, obj)

class CustomerAdmin(admin.ModelAdmin):
    list_display = ( 'phone_number', 'user_email', 'phone_number', 'is_active')
    search_fields = ('user__username', 'user__email', 'phone_number')
    readonly_fields = ('user_email', 'user_first_name', 'user_last_name','gender','phone_number','birthday')  # Adding related fields as readonly

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
    )
    
    
#     fields = ['name', 'email', 'gender', 'birthday', 'is_active']

#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         if obj:  # Editing an existing customer
#             form.base_fields.pop('password', None)  # Remove 'password' field from the form
#         return form

#     # Allow only the 'active' field to be editable by the admin
#     def get_readonly_fields(self, request, obj=None):
#         if obj:  # Editing an existing customer
#             return ['name', 'email', 'gender', 'birthday']
#         return super().get_readonly_fields(request, obj)
    
#     inlines = [AddressInline]

admin.site.register(Customer, CustomerAdmin)
