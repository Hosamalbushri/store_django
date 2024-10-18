from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
import os
from django.dispatch import receiver

class Category(MPTTModel):
    
    STATUS_CHOICES = (
        ('1', 'On'),
        ('0', 'Off'),
    )
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children'
    )
    image = models.ImageField(upload_to='Categories/photos/%y/%m/%d')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='1')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        # Convert the product name to uppercase before saving
        self.name = self.name.title()
        super(Category, self).save(*args, **kwargs)
        self.update_children_status()
        
        
    
    def clean(self):
        super().clean()
        if self.parent:
            if self.parent == self:
                raise ValidationError("القسم لا يمكن أن يكون أبًا لنفسه.")
            
            if self.parent.is_descendant_of(self):
                raise ValidationError("لا يمكن أن يكون القسم أبًا لأي من أسلافه.")
    def update_children_status(self):
        """Updates the status of all child categories to match the current category's status."""
        children = self.get_descendants()
        for child in children:
            child.status = self.status
            child.save()    

    def delete(self, *args, **kwargs):
        """Prevents deletion if the category has children."""
        if self.get_children().exists():
            raise ValidationError("لا يمكن حذف القسم لأنه يحتوي على أقسام فرعية.")
        super().delete(*args, **kwargs)
           
        
# Signal to delete the image file when the Product instance is deleted
@receiver(models.signals.post_delete, sender=Category)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `Product` object is deleted."""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)        
            
@receiver(models.signals.pre_save, sender=Category)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes old file from filesystem when corresponding `Product` object is updated with a new file."""
    if not instance.pk:
        return False

    try:
        old_image = Category.objects.get(pk=instance.pk).image
    except Category.DoesNotExist:
        return False

    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)
                       
############################ End  Category class ###################################################          

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    status = models.CharField(max_length=10, choices=(('on', 'On'), ('off', 'Off')), default='off')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert the product name to Title Case (first letters capitalized)
        self.name = self.name.title()
        super(Product, self).save(*args, **kwargs)

    def clean(self):
      super().clean()
    # Ensure the product belongs to child categories only (not parent categories)
      if self.category.get_children().exists():  # MPTT method to check if category has children
        raise ValidationError("لا يمكن ربط المنتج بفئة رئيسية، فقط الفئات الفرعية مسموح بها.")   #
    
    
    
    

# ProductImage model to store multiple photos for a product
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='Products/photos/%y/%m/%d')  # Image is required

    def __str__(self):
        return f"{self.product.name} - Image"
    
    
    def clean(self):
        # Check image size
        if self.image.size > 2 * 1024 * 1024:  # 2 MB
            raise ValidationError("The maximum file size allowed is 2 MB.")

# Signal to delete the image file when the ProductImage instance is deleted
@receiver(models.signals.post_delete, sender=ProductImage)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `ProductImage` object is deleted."""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

# Signal to delete the old image file when the ProductImage is updated with a new file
@receiver(models.signals.pre_save, sender=ProductImage)
def auto_delete_image_on_change(sender, instance, **kwargs):
    """Deletes old file from filesystem when corresponding `ProductImage` object is updated with a new file."""
    if not instance.pk:
        return False

    try:
        old_image = ProductImage.objects.get(pk=instance.pk).image
    except ProductImage.DoesNotExist:
        return False

    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)  