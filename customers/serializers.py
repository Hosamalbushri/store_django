# your_app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer
from .models import Address
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

class RegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)  # تشفير كلمة المرور
        user.save()

        Customer.objects.create(
            user=user,
           
        )

        return user
    
    
@csrf_exempt
@api_view(['POST'])
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_type', 'street_address', 'city', 'state', 'postal_code', 'country']

    def create(self, validated_data):
        customer = self.context['request'].user.customer  # Get customer linked to the authenticated user
        validated_data['customer'] = customer  # Set the customer field
        return super().create(validated_data)    
    