# models.py
from django.conf import settings
from django.db import models

from customers.models import Address
from products.models import Product


class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery')
    ]
    name = models.CharField(max_length=50, choices=PAYMENT_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)  # Optional description

    def __str__(self):
        return self.get_name_display()
    
    

class Order(models.Model):
    # Status choices for the order
    class Status(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        COMPLETED = 'Completed', 'Completed'
        CANCELED = 'Canceled', 'Canceled'
        SHIPPED = 'Shipped', 'Shipped'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="orders")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE,related_name="orders")  # Linking PaymentMethod
    order_number = models.PositiveIntegerField(unique=True, editable=False)  # Add order number field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Order {self.order_number} for {self.user.username}"
    
    
    def save(self, *args, **kwargs):
        
        if not self.order_number:
            # Get the maximum order number and increment by 1, or start with 1 if no orders exist
            last_order = Order.objects.all().order_by('order_number').last()
            self.order_number = last_order.order_number + 1 if last_order else 1
        super().save(*args, **kwargs)

    def total_price(self):
        # Calculate the total price of all items in the order
        return sum(item.total_price() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    product_description = models.TextField(blank=True, null=True)  # Store product description
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_attributes = models.JSONField(null=True, blank=True) 
    def __str__(self):
        return f"Order {self.order.order_number} for {self.order.user.username}"   
    
    def save(self, *args, **kwargs):
        # Set the price to the discounted price from the Product model
        if not self.price:
            self.price = self.product.get_price_after_discount()
        super(OrderItem, self).save(*args, **kwargs)

    def total_price(self):
        return self.price * self.quantity