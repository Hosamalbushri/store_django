from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Product, ProductImage,Attribute, SubAttribute
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms


# Register your models here.
from .models import Category

class CategoryAdmin(DraggableMPTTAdmin):
   
    mptt_indent_field = "name"
    list_display = ('tree_actions', 'indented_title','status')
    list_display_links = ('indented_title',)

    def save_model(self, request, obj, form, change):
        obj.full_clean()  # يضمن تشغيل دالة clean قبل الحفظ
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
    # extra = 8  # Number of empty forms to display

# Custom admin for Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'status')
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

    # def has_delete_permission(self, request, obj=None):
    #     """
    #     Prevent deletion of products if they have related images.
    #     """
    #     if obj and obj.images.exists():
    #         messages.error(request, f"لا يمكن حذف المنتج '{obj.name}' لأنه يحتوي على صور.")
    #         return False
    #     return super().has_delete_permission(request, obj)

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
        if self.instance.pk:  # Instance already exists (editing)
            attribute_type = self.instance.parent_attribute.attribute_type
            
            # Show the 'value' field based on the parent attribute type
            self._update_value_field(attribute_type)
        else:  # Creating a new instance
            # Hide the 'value' field for new SubAttributes
            self.fields['value'].widget = forms.HiddenInput()

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
    extra = 0  # Number of blank forms to display
    # def has_add_permission(self, request, obj=None):
    #     return False  # Prevent adding new SubAttributes from here

    # def has_change_permission(self, request, obj=None):
    #     return True  # Allow changing existing SubAttributes
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

admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
