# views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order, OrderItem, Product, Address
from .serializers import OrderItemSerializer, OrderSerializer

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        shipping_address_id = request.data.get('shipping_address')
        items_data = request.data.get('items')

        # Validate shipping address
        try:
            shipping_address = Address.objects.get(id=shipping_address_id, user=user)
        except Address.DoesNotExist:
            return Response({"detail": "Invalid shipping address."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order with recipient details
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address
        )

        # Add items to the order with attributes
        for item_data in items_data:
            product_id = item_data.get('product')
            quantity = item_data.get('quantity', 1)
            product_attributes = item_data.get('product_attributes', {})

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"detail": f"Product with id {product_id} not found."}, status=status.HTTP_400_BAD_REQUEST)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price,
                product_attributes=product_attributes
            )

        # Serialize the order to return in the response
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    
    
class OrderUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Limit access to orders belonging to the requesting user
        return Order.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        # Retrieve the order
        order = self.get_object()

        # Ensure the status is 'Pending' before allowing updates
        if order.status != Order.Status.PENDING:
            return Response(
                {"detail": "Only orders with 'Pending' status can be edited."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # If 'Pending', proceed with the update
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(order, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)   
    
    
class OrderItemUpdateView(generics.UpdateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)

    def update(self, request, order_id, item_id, *args, **kwargs):
        try:
            order_item = self.get_queryset().get(id=item_id, order__id=order_id)
        except OrderItem.DoesNotExist:
            return Response({"detail": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order_item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)    



class OrderListRetrieveView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Restrict to orders for the authenticated user
        return Order.objects.filter(user=self.request.user)

    def get(self, request, order_id=None, *args, **kwargs):
        # If `order_id` is provided, retrieve a single order
        if order_id:
            try:
                order = self.get_queryset().get(id=order_id)
            except Order.DoesNotExist:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(order)
            return Response(serializer.data)

        # Otherwise, return all orders for the user
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
    
    
    
    
    
class OrderListRetrieveDeleteView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Restrict to orders for the authenticated user
        return Order.objects.filter(user=self.request.user)

    def get(self, request, order_id=None, *args, **kwargs):
        # If `order_id` is provided, retrieve a single order
        if order_id:
            try:
                order = self.get_queryset().get(id=order_id)
            except Order.DoesNotExist:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(order)
            return Response(serializer.data)

        # Otherwise, return all orders for the user
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def delete(self, request, order_id=None, *args, **kwargs):
        # If `order_id` is provided, delete the order
        if order_id:
            try:
                order = self.get_queryset().get(id=order_id)
            except Order.DoesNotExist:
                return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check if the order status is 'Pending' before deleting
            if order.status != Order.Status.PENDING:
                return Response({"detail": "Only pending orders can be deleted."}, status=status.HTTP_400_BAD_REQUEST)

            order.delete()
            return Response({"detail": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Order ID must be provided."}, status=status.HTTP_400_BAD_REQUEST)

class OrderItemDeleteView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)

    def delete(self, request, order_id, item_id, *args, **kwargs):
        try:
            order_item = self.get_queryset().get(id=item_id, order__id=order_id)
        except OrderItem.DoesNotExist:
            return Response({"detail": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the order item
        order_item.delete()
        return Response({"detail": "Order item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)    