from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from products.models import Product

class Customer(models.Model):
    user = models.OneToOneField(User, related_name='user' ,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)  
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birthday = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='customers/photos/%Y/%m/%d/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # objects = CustomerManager()

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['name']

    # class Meta:
    #     verbose_name = 'Customer'
    #     verbose_name_plural = 'Customers'

    def __str__(self):
        return self.user.username

    def clean(self):
        # Optionally, you can add custom validation here (e.g., validate email or birthday)
        pass
    
    





class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")  # Link to User, not Customer
    name = models.CharField(max_length=100)  # Recipient's name
    email = models.EmailField()  # Recipient's email
    phone_number = models.CharField(max_length=15)  # Recipient's phone number
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)  # Optional: to mark default address
    
    def save(self, *args, **kwargs):
        # Capitalize the specified fields before saving
        if self.name:
            self.name = self.name.title()
        if self.street:
            self.street = self.street.title()
        if self.city:
            self.city = self.city.title()
        if self.country:
            self.country = self.country.title()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, {self.street}, {self.city},{self.country} - {self.postal_code}" 
    
    
    
    
class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevents duplicate favorites for the same user-product pair
        ordering = ['-created_at']  # Shows most recent favorites first

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"    
    
    
    
    

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def total_price(self):
        # Calculate the total price of items in the cart
        return sum(item.total_price() for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.name} in cart"

    def total_price(self):
        # Use the discounted price if there’s a discount; otherwise, use the regular price
        discounted_price = self.product.get_price_after_discount()
        return discounted_price * self.quantity