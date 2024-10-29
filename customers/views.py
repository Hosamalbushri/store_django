from django.shortcuts import get_object_or_404
from rest_framework import generics

from products.models import Product
from .serializers import CartItemSerializer, CartSerializer, CustomTokenObtainPairSerializer, CustomerProfileSerializer, FavoriteSerializer, PasswordChangeSerializer, RegisterSerializer, UserSerializer
from rest_framework.permissions import AllowAny ,IsAuthenticated
from django.contrib.auth.models import User
from rest_framework import viewsets
from .models import Address, Cart, CartItem, Customer, Favorite
from .serializers import AddressSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view ,permission_classes
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import ValidationError
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
    
    
    
class FavoriteListCreateView(generics.ListCreateAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Show only the authenticated user's favorites
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data.get('product')
        # Check if the product is already favorited by this user
        if Favorite.objects.filter(user=self.request.user, product=product).exists():
            return Response({"detail": "Product is already in favorites."}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=self.request.user)


class FavoriteDeleteView(generics.DestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Ensure that only the user's own favorite can be deleted
        product_id = self.kwargs['product_id']
        favorite = get_object_or_404(Favorite, user=self.request.user, product__id=product_id)
        return favorite    
    
    
    
class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get or create a cart for the user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

class AddToCartView(generics.CreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Get or create the user's cart
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Retrieve and validate product ID from the request data
        product_id = request.data.get('product')
        if not product_id:
            raise ValidationError({"product": "This field is required."})

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise ValidationError({"product": "Product not found."})

        # Retrieve quantity or set default to 1 if not provided
        quantity = request.data.get('quantity', 1)
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValidationError({"quantity": "Quantity must be a positive integer."})

        # Check if the product is already in the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity  # Increment quantity if item already exists
        else:
            cart_item.quantity = quantity  # Set initial quantity if new item

        cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)

class UpdateCartItemView(generics.UpdateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart = get_object_or_404(Cart, user=self.request.user)
        return get_object_or_404(CartItem, cart=cart, product__id=self.kwargs['product_id'])

    def patch(self, request, *args, **kwargs):
        cart_item = self.get_object()
        quantity = request.data.get('quantity', 1)
        cart_item.quantity = quantity
        cart_item.save()
        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_200_OK)

class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart = get_object_or_404(Cart, user=self.request.user)
        return get_object_or_404(CartItem, cart=cart, product__id=self.kwargs['product_id'])    