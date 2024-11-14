from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.core.exceptions import ValidationError
import os
from django.dispatch import receiver
from django.utils import timezone
from filer.fields.image import FilerImageField



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
    image = FilerImageField(null=True, blank=True, related_name="category_images", on_delete=models.SET_NULL)
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
        # Convert the  name to uppercase before saving
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
        return f"( {self.parent_attribute.name} )-->{self.name}".strip()     
    ############################ End  Attribute class ###################################################          

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    logo = FilerImageField(null=True, blank=True, related_name="brand_images", on_delete=models.SET_NULL)

    def __str__(self):
        return self.name

 

    def save(self, *args, **kwargs):
        self.name = self.name.title()
        super(Brand, self).save(*args, **kwargs)


 
    
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
    
    
    def delete(self, *args, **kwargs):
        # Check if the product has related OrderItems, CartItems, or Favorites
        if self.order_items.exists() or self.cart_items.exists() or self.favorites.exists():
            raise ValidationError("This product is associated with an order, cart, or favorite. You cannot delete it.")
        super().delete(*args, **kwargs)


    def __str__(self):
        return self.name


    
    def save(self, *args, **kwargs):
        # Convert the product name to Title Case (first letters capitalized)
        self.name = self.name.title()
        super(Product, self).save(*args, **kwargs)
    
    

# ProductImage model to store multiple photos for a product
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = FilerImageField(related_name="product_images",on_delete=models.SET_NULL,null=True, blank=True)  # Image is required
    

    def __str__(self):
        return f"{self.product.name} - Image"
    
            
###################### End Product Class ################################
