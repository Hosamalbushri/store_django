from rest_framework import generics
from .serializers import CustomTokenObtainPairSerializer, CustomerProfileSerializer, PasswordChangeSerializer, RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny ,IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Address, Customer
from .serializers import AddressSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # To bypass CSRF check for API requests


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    
    
class CustomerProfileView(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the current user, which also fetches the associated Customer instance
        return self.request.user 
    
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Set the new password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





    
# List and create addresses for the authenticated user
class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return addresses for the logged-in user
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the logged-in user
        serializer.save(user=self.request.user)

# Retrieve, update, or delete a specific address by ID
class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Restrict queryset to the logged-in user's addresses
        return Address.objects.filter(user=self.request.user)