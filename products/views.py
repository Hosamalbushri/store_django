from rest_framework.response import Response
from rest_framework import viewsets, permissions ,generics ,status
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class CategoryListView(APIView):
    def get(self, request):
        # Retrieve only top-level categories (without a parent) to start the tree structure
        top_categories = Category.objects.filter(parent=None, status='1')  # Filter for active categories
        serializer = CategorySerializer(top_categories, many=True)
        return Response(serializer.data)
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow access to any user

    
class CategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.filter(status='1').get(id=pk)

            # Check if the category is a parent (has children)
            if category.parent is None:  # Means it's a parent category
                serializer = CategorySerializer(category)
                return Response(serializer.data)
            else:
                return Response({"error": "The category is not a parent."}, status=status.HTTP_400_BAD_REQUEST)

        except Category.DoesNotExist:
            return Response({"error": "Category not found."}, status=status.HTTP_404_NOT_FOUND)
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allow access to any user
     
    
    
    
    

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('category').filter(status='1').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Allow access to any user
    
    
    
class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(status='1').all()  # Queryset for all products
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
        return Product.objects.filter(category_id=category_id,status='1')  # Filter products by category

    def get(self, request, *args, **kwargs):
        # Call the get_queryset method to get products by category
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)  # Serialize the products
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return serialized data
        else:
            return Response({"detail": "No products found for this category."}, status=status.HTTP_404_NOT_FOUND)    