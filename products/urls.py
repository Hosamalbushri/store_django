from django.urls import path ,include
from. import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import routers
from .views import CategoryDetailView, CategoryListView , ProductViewSet , ProductDetailView ,ProductsByCategoryView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    
    path('', include(router.urls)),  # إضافة نهايات API تحت مسار /api/
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),  # Endpoint to get product by ID
    path('products/category/<int:category_id>/', ProductsByCategoryView.as_view(), name='products-by-category'),  # Endpoint to get products by category
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
]
