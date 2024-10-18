from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from .models import Category,Product, ProductImage
from django.contrib import messages
from django.core.exceptions import ValidationError


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
    extra = 8  # Number of empty forms to display

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

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
