from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Product, ProductImage,Attribute,SubAttribute ,Brand,Discount
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms
from django.utils.html import format_html , mark_safe


# Register your models here.
from .models import Category

class CategoryAdmin(DraggableMPTTAdmin):
   
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title','status','image_tag')
    list_display_links = ('indented_title','image_tag')
    list_editable=['status']

    
    def image_tag(self, obj):
        
     if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: 100px; border-radius: 50"/>'.format(obj.image.url))
     return "No Image"  # Fallback if no image is present

    
    image_tag.short_description = 'Current Image'
    
    
    fieldsets = (
        ('Category Info', {
        'fields': (
        'name',
        'parent',
        'status',
        ),
        
        }),
        
        ('Category Image', {
        'fields': (
        'image',
        ),
        # "classes": ["wide", "collapse"],

        })
       
      

    )
        

    
    def save_model(self, request, obj, form, change):
        obj.full_clean()  
        super().save_model(request, obj, form, change)
        
        
    def has_delete_permission(self, request, obj=None):
        """
        Override delete permission to block deletion if the category has children.
        """
        if obj and obj.get_children().exists():
            # Prevent deletion and show an error message
            # messages.error(request, f"لا يمكن حذف القسم '{obj.name}' لأنه يحتوي على أقسام فرعية.")
            return False
        return super().has_delete_permission(request, obj)

    def delete_model(self, request, obj):
        """
        Custom delete logic: Prevent deletion if category has children.
        """   
        if obj.get_children().exists():
            # Display an error message and prevent deletion
            messages.error(request, f"لا يمكن حذف القسم '{obj.name}' لأنه يحتوي على أقسام فرعية.")
        else:
            super().delete_model(request, obj)
   
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display
  


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        
        # Validate category exists
        if not category:
            raise ValidationError("Please select a category for the product.")
        
        # Ensure the product is assigned only to a subcategory, not a parent category
        if category and category.get_children().exists():  # Assuming MPTT is used
            raise ValidationError("Cannot assign a product to a parent category. Only subcategories are allowed.")
        
        return cleaned_data
    
    
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm  # Link the custom form to ProductAdmin
    list_display = ('name', 'category', 'status','get_price_after_discount')
    inlines = [ProductImageInline]  # Attach ProductImageInline to ProductAdmin
    list_per_page = 50    
    # save_on_top = True
    list_display_links = ('name','get_price_after_discount')
    list_editable=('status','category')
    # view_on_site = False



    
    def save_model(self, request, obj, form, change):
        # Format name to title case
        obj.name = obj.name.title()
        if obj.pk and not obj.category:
            raise ValidationError("Please select a category for the product.")
     
        
    # Ensure the product belongs to child categories only (not parent categories)
        if obj.category.get_children().exists():  # MPTT method to check if category has children
           raise ValidationError("Cannot assign a product to a parent category. Only subcategories are allowed.")   #
        super().save_model(request, obj, form, change)
        
     
        




####################################### Attribute ######################################################################################
class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If the object exists (editing mode), disable the `attribute_type` field
        if self.instance and self.instance.pk:
            self.fields['attribute_type'].widget.attrs['readonly'] = True  # Make field readonly
            self.fields['attribute_type'].widget.attrs['disabled'] = True  # Disable field
            # Optionally, hide the field entirely
            self.fields['attribute_type'].widget = forms.HiddenInput()
            
class SubAttributeForm(forms.ModelForm):
    class Meta:
        model = SubAttribute
        fields = '__all__'
        
           

    def __init__(self, *args, **kwargs):
        super(SubAttributeForm, self).__init__(*args, **kwargs)
        
        # Check if we're editing an existing instance
        if self.instance.pk:  # instance already exists
            attribute_type = self.instance.parent_attribute.attribute_type
            
            # Change the 'value' field based on the parent attribute type
            self._update_value_field(attribute_type)

        # If creating a new instance, check the parent attribute from the data
        elif 'parent_attribute' in self.data:
            try:
                parent_attribute = Attribute.objects.get(pk=self.data['parent_attribute'])
                attribute_type = parent_attribute.attribute_type
                self._update_value_field(attribute_type)
            except Attribute.DoesNotExist:
                pass  # Handle the case where the parent attribute does not exist

    def _update_value_field(self, attribute_type):
        """Update the value field widget based on the parent attribute type."""
        if attribute_type == 'text':
            self.fields['value'].widget = forms.TextInput(attrs={'class': 'form-control'})
        elif attribute_type == 'number':
            self.fields['value'].widget = forms.NumberInput(attrs={'class': 'form-control'})
        elif attribute_type == 'color':
            self.fields['value'].widget = forms.TextInput(attrs={'type': 'color'})
            
# Tabular inline for SubAttribute
class SubAttributeInline(admin.TabularInline):
    model = SubAttribute
    form = SubAttributeForm
    
    list_display = ('name', 'value')
    


    extra = 0  # Number of blank forms to display
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # You can customize the formset if needed
        return formset

class AttributeAdmin(admin.ModelAdmin):
    form = AttributeForm
    list_display = ('name', 'attribute_type')
    inlines = [SubAttributeInline]  # Attach SubAttributeInline to Attribute admin
    def get_inline_instances(self, request, obj=None):
        inlines = super().get_inline_instances(request, obj)
        # Only show SubAttributeInline when editing an existing Attribute
        if obj is None:
            return []  # Hide inlines for new Attribute creation
        return inlines
###########################################################################################################

class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'thumbnail')
    search_fields = ('name',)

    
   
    def thumbnail(self, obj):
        """Display the image thumbnail in the admin list."""
        if obj.logo:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.logo.url)
        return "No Image"  # Fallback if no image is present

    thumbnail.short_description = 'Image' 

    
    
    
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'value', 'start_date', 'end_date', 'active')
    list_filter = ('discount_type', 'active')
    list_display_links = ('discount_type','start_date','end_date')
    search_fields = ('value',)   
    list_editable=('value',)



    
  
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Discount, DiscountAdmin)



