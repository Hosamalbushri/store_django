from django.urls import path ,include
from .views import AddressListCreateView, AddressRetrieveUpdateDestroyView, CustomTokenObtainPairView, CustomerProfileView, RegisterView, change_password, update_user_profile
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
    path('addresses/<int:pk>/', AddressRetrieveUpdateDestroyView.as_view(), name='address_detail_update_delete')
]