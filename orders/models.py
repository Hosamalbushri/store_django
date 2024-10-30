# models.py
from django.conf import settings
from django.db import models

from customers.models import Address
from products.models import Product

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

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
        return f"{self.quantity} of {self.product.name} in order {self.order.id}"

    def total_price(self):
        return self.price * self.quantity
