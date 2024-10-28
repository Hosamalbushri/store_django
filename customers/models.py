from django.db import models
from django.contrib.auth.models import User

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