from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    customer = models.ForeignKey(User, related_name='addresses', on_delete=models.CASCADE)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.customer.username} - {self.address_type.capitalize()} Address"    