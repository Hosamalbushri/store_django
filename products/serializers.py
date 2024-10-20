from rest_framework import serializers
from .models import Category, Product, ProductImage, SubAttribute, Attribute

class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.PrimaryKeyRelatedField(source='parent', read_only=True)  # Parent Category ID
    parent_name = serializers.CharField(source='parent.name', read_only=True)  # Parent Category Name

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent_id', 'parent_name']  # Reordered fields for clarity

class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = ['id', 'name']  # Keeping it simple

class SubAttributeSerializer(serializers.ModelSerializer):
    parent_attribute = AttributeSerializer()  # Nested AttributeSerializer for parent attribute

    class Meta:
        model = SubAttribute
        fields = ['id', 'name', 'value', 'parent_attribute']  # Reordered for clarity

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['image_url']  # Only return the image URL

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)  # Nested CategorySerializer
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )  # For write operations

    images = ProductImageSerializer(many=True, read_only=True)  # Nested ProductImageSerializer
    brand_name = serializers.CharField(source='brand.name')  # Get the brand name directly
    attributes = SubAttributeSerializer(many=True, read_only=True)  # Nested SubAttributeSerializer
    price_after_discount = serializers.SerializerMethodField()  # Add a method field for the discounted price

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'price_after_discount', 'brand_name', 'category', 'category_id', 'images', 'attributes']  # Reordered for clarity

    def get_price_after_discount(self, obj):
        """Calculate and return the price after applying the discount."""
        if obj.discount and obj.discount.is_valid():
            if obj.discount.discount_type == 'percentage':
                discount_amount = (obj.discount.value / 100) * obj.price
                return obj.price - discount_amount
            elif obj.discount.discount_type == 'fixed':
                return obj.price - obj.discount.value
        return obj.price  # Return the original price if no discount is applicable