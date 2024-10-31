from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
import os
from django.dispatch import receiver
from django.utils import timezone



############################ Begin  Category class ###################################################          

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
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])
    
    
    def save(self, *args, **kwargs):
        # Convert the product name to uppercase before saving
        self.name = self.name.title()
        super(Category, self).save(*args, **kwargs)
        self.update_children_status()
        
        
    
    def clean(self):
        super().clean()
        if self.parent:
            if self.parent == self:
                raise ValidationError("A category cannot be its own parent.")
            
            if self.parent.is_descendant_of(self):
                raise ValidationError("A category cannot be a parent of its ancestors.")
    def update_children_status(self):
        """Updates the status of all child categories to match the current category's status."""
        children = self.get_descendants()
        for child in children:
            child.status = self.status
            child.save()    

    def delete(self, *args, **kwargs):
        if self.products.exists():
            raise ValidationError("This category has products associated with it and cannot be deleted.")
        
        """Prevents deletion if the category has children."""
        if self.get_children().exists():
            raise ValidationError("This category has subcategories and cannot be deleted.")
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



############################ Begin  Attribute class ###################################################          


ATTRIBUTE_TYPE_CHOICES = [
    ('text', 'Text'),
    ('number', 'Number'),
    ('color', 'Color'),
]

class Attribute(models.Model):
    name = models.CharField(max_length=100,unique=True)
    attribute_type = models.CharField(max_length=10, choices=ATTRIBUTE_TYPE_CHOICES)
    
    
    def save(self, *args, **kwargs):
        # Convert the product name to uppercase before saving
        self.name = self.name.title()
        super(Attribute, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubAttribute(models.Model):
    parent_attribute = models.ForeignKey(Attribute, related_name='sub_attributes', on_delete=models.CASCADE)
    name = models.CharField(max_length=100,unique=True)
    value = models.CharField(max_length=100 , blank=True, null=True) 
    
    
    def save(self, *args, **kwargs):
        # Convert the product name to uppercase before saving
        self.name = self.name.upper()
        super(SubAttribute, self).save(*args, **kwargs)
    
    def clean(self):
        # Ensure the attribute_type matches the parent attribute's type
        if not self.parent_attribute:
            raise ValidationError("SubAttribute must be linked to a parent Attribute.")

    @property
    def attribute_type(self):
        return self.parent_attribute.attribute_type

    def __str__(self):
        return f"( {self.parent_attribute.name} )-->{self.name} "
    
    ############################ End  Attribute class ###################################################          

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/logos/%y/%m/%d', blank=False, null=False)  # Ensure logo is required

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        # Custom validation for logo field, for example, check size
        if self.logo and self.logo.size > 2 * 1024 * 1024:  # 2 MB max size
            raise ValidationError("The maximum file size allowed for the logo is 2 MB.")

    def save(self, *args, **kwargs):
        # Automatically delete the old file when replacing with a new one
        try:
            this = Brand.objects.get(id=self.id)
            if this.logo != self.logo and os.path.isfile(this.logo.path):
                os.remove(this.logo.path)
        except Brand.DoesNotExist:
            pass  # This is a new object, so no need to delete an old logo
        self.name = self.name.title()
        super(Brand, self).save(*args, **kwargs)


# Signal to delete the logo file when a Brand instance is deleted
@receiver(models.signals.post_delete, sender=Brand)
def auto_delete_logo_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `Brand` object is deleted."""
    if instance.logo:
        if os.path.isfile(instance.logo.path):
            os.remove(instance.logo.path)     
    
####################################################################################################

class Discount(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    value = models.DecimalField(max_digits=5, decimal_places=2)  # Discount value
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.value}% off"
        return f"{self.value} currency units off"

    def clean(self):
        # Ensure the end date is after the start date
        if self.end_date <= self.start_date:
            raise ValidationError("The end date must be after the start date.")
        
        # Ensure the discount is active within the valid time frame
        if self.active and (self.start_date > timezone.now() or self.end_date < timezone.now()):
            raise ValidationError("Cannot activate a discount outside the valid time range.")

    def is_valid(self):
        """Returns True if the discount is currently active and valid."""
        now = timezone.now()
        return self.active and self.start_date <= now <= self.end_date    
    
    
    
############################ Begin  Product class ###################################################          
       

class Product(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=False, null=False)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=1, choices=(('1', 'On'), ('0', 'Off')), default='1')
    attributes = models.ManyToManyField(SubAttribute, blank=True)
    
    
    def get_price_after_discount(self):
        """Calculate and return the price after applying the discount."""
        if self.discount and self.discount.is_valid():
            if self.discount.discount_type == 'percentage':
                discount_amount = (self.discount.value / 100) * self.price
                return self.price - discount_amount
            elif self.discount.discount_type == 'fixed':
                return self.price - self.discount.value
        return self.price


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert the product name to Title Case (first letters capitalized)
        self.name = self.name.title()
        super(Product, self).save(*args, **kwargs)

    def clean(self):
      super().clean()
      
      if not self.category:
            raise ValidationError("Please select a category for the product.")
        
    # Ensure the product belongs to child categories only (not parent categories)
      if self.category.get_children().exists():  # MPTT method to check if category has children
        raise ValidationError("Cannot assign a product to a parent category. Only subcategories are allowed.")   #
    
    
    
    

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
            
###################### End Product Class ################################
