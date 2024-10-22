from django.db import models

class Customer(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)  # The password will be handled by AbstractBaseUser
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    birthday = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='customers/photos/%Y/%m/%d/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # objects = CustomerManager()

    # USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'

    def __str__(self):
        return self.name

    def clean(self):
        # Optionally, you can add custom validation here (e.g., validate email or birthday)
        pass
    
    





class Address(models.Model):
    ADDRESS_TYPE_CHOICES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    customer = models.ForeignKey(Customer, related_name='addresses', on_delete=models.CASCADE)
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.customer.name} - {self.address_type.capitalize()} Address"    