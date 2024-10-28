# your_app/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer
from .models import Address
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Call the original validate method to get user and token
        data = super().validate(attrs)

        # Check if user is active in the Customer model
        user = self.user
        try:
            customer = Customer.objects.get(user=user)
            if not customer.is_active:
                raise serializers.ValidationError("This account is inactive. Please contact support.")
        except Customer.DoesNotExist:
            raise serializers.ValidationError("Customer profile does not exist.")

        return data

class RegisterSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)  
        user.save()

        Customer.objects.create(
            user=user,
           
        )

        return user
    
    

class CustomerProfileSerializer(serializers.ModelSerializer):
    gender_display = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ['id','gender' ,'gender_display','phone_number','birthday','photo']
        
        
    def get_gender_display(self, obj):
        # Map abbreviations to full gender names
        return 'Female' if obj.gender == 'F' else 'Male' if obj.gender == 'M' else 'Other'    
        
        
class UserSerializer(serializers.ModelSerializer):
    details = CustomerProfileSerializer(source='user')
    class Meta:
        model = User
        fields = ['id','username', 'first_name', 'last_name','email','details']  # Add other fields as needed

    def update(self, instance, validated_data):
        # Extract nested data for the customer profile
        customer_data = validated_data.pop('user', None)
        
        # Update User fields
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        # Update the Customer profile fields if provided
        if customer_data:
            Customer.objects.filter(user=instance).update(**customer_data)

        return instance

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({"old_password": "Old password is incorrect"})
        return data    
 
    
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'user', 'name', 'email', 'phone_number','country', 'city', 'street', 'postal_code', 'is_default']
        read_only_fields = ['user']  
    