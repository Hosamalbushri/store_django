from django.urls import path ,include
from .views import AddToCartView, AddressListCreateView, AddressRetrieveUpdateDestroyView, CartView, CustomTokenObtainPairView, CustomerProfileView, FavoriteDeleteView, FavoriteListCreateView, RegisterView, RemoveFromCartView, UpdateCartItemView, change_password, update_user_profile
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 
from rest_framework.routers import DefaultRouter


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', CustomerProfileView.as_view(), name='customer-profile'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('profile/change-password/', change_password, name='change_password'),
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressRetrieveUpdateDestroyView.as_view(), name='address_detail_update_delete'),
    
    
    path('favorites/', FavoriteListCreateView.as_view(), name='favorite-list-create'),
    path('favorites/<int:product_id>/delete/', FavoriteDeleteView.as_view(), name='favorite-delete'),
    
    path('cart/', CartView.as_view(), name='cart-view'),
    path('cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('cart/update/<int:product_id>/', UpdateCartItemView.as_view(), name='cart-update'),
    path('cart/remove/<int:product_id>/', RemoveFromCartView.as_view(), name='cart-remove'),
]