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
    list_display_links = ('indented_title',)
    
    
    def image_tag(self, obj):
        return format_html('<img src="{}" style="width: 50px; height: 50px; border-radius: 50"/>'.format(obj.image.url))
    
    image_tag.short_description = 'Current Image'
        

    
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
    extra = 0  # Number of empty forms to display

# Custom admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status','get_price_after_discount')
    inlines = [ProductImageInline]  # Attach ProductImageInline to ProductAdmin
    

    
    
    def save_related(self, request, objs, *args, **kwargs):
        super().save_related(request, objs, *args, **kwargs)
        
        # for product in objs:
        #     # Validate the number of images
        #     if product.images.count() > 8:
        #         raise ValidationError("A product can have a maximum of 8 images.")

    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure product name is title cased.
        """
        obj.name = obj.name.title()
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
        # self.fields['value'].label = 'Custom Value Label'  # Change this to the desired label

        
        # # Check if we're editing an existing instance
        # if self.instance.pk:  # Instance already exists (editing)
        #     attribute_type = self.instance.parent_attribute.attribute_type
            
        #     # Show the 'value' field based on the parent attribute type
        #     self._update_value_field(attribute_type)
        # else:  # Creating a new instance
        #     # Hide the 'value' field for new SubAttributes
        #     self.fields['value'].widget = forms.HiddenInput()


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
    list_display = ('name', 'logo_tag')
    search_fields = ('name',)
    
    def logo_tag(self, obj):
        return format_html('<img src="{}"  style="width: 50px; height: 50px; border-radius: 50"/>'.format(obj.logo.url))

    
    
    
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_type', 'value', 'start_date', 'end_date', 'active')
    list_filter = ('discount_type', 'active')
    search_fields = ('value',)   
    
    
    
  
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Discount, DiscountAdmin)



