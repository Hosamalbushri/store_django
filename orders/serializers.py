# serializers.py
from rest_framework import serializers
from .models import Order, OrderItem, PaymentMethod



class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description'] 



class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total_price', 'product_attributes']
        read_only_fields = ['price', 'total_price', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.ReadOnlyField()
    shipping_address_details = serializers.ReadOnlyField(source="shipping_address.full_address")
    payment_method = serializers.PrimaryKeyRelatedField(queryset=PaymentMethod.objects.all(), required=True)

    

    class Meta:
        model = Order
        fields = [
            'id', 'user',
            'status', 'shipping_address', 'shipping_address_details','payment_method','items', 'total_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'status', 'total_price', 'created_at', 'updated_at']
            
    def validate(self, data):
        # Ensure that the payment field is provided when creating a new order
        if self.instance is None and not data.get('payment_method'):
            raise serializers.ValidationError({"payment": "Payment is required when creating an order."})
        return data
        
        
    def update(self, instance, validated_data):
        # Check if the order status is 'Pending'
        if instance.status != Order.Status.PENDING:
            raise serializers.ValidationError("Only orders with 'Pending' status can be edited.")

        # Update the Order fields
        instance.shipping_address = validated_data.get('shipping_address', instance.shipping_address)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        # Update the OrderItems if they are provided
        items_data = validated_data.get('items')
        if items_data:
            for item_data in items_data:
                item_id = item_data.get('id')
                if item_id:
                    # Update existing OrderItem
                    order_item = instance.items.get(id=item_id)
                    order_item.quantity = item_data.get('quantity', order_item.quantity)
                    order_item.product_attributes = item_data.get('product_attributes', order_item.product_attributes)
                    order_item.save()
                else:
                    # Add a new OrderItem if no ID is provided
                    OrderItem.objects.create(order=instance, **item_data)

        return instance
