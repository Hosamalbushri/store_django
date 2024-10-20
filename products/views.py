from rest_framework.response import Response
from rest_framework import viewsets, permissions ,generics ,status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint لعرض وإنشاء وتحديث وحذف الفئات.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow access to any user
    
    
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()  # Queryset for all products
    serializer_class = ProductSerializer  # Use the ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow access to any user

    def get(self, request, *args, **kwargs):
        product = self.get_object()  # Retrieve the product instance
        serializer = self.get_serializer(product)  # Serialize the product
        return Response(serializer.data)     



class ProductsByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow access to any user
    def get_queryset(self):
        category_id = self.kwargs['category_id']  # Get the category ID from URL
        return Product.objects.filter(category_id=category_id)  # Filter products by category

    def get(self, request, *args, **kwargs):
        # Call the get_queryset method to get products by category
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)  # Serialize the products
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return serialized data
        else:
            return Response({"detail": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)    