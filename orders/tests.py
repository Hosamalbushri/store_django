from datetime import timedelta, timezone
from django.test import TestCase

from django.contrib.auth import get_user_model
from products.models import Discount, Product
from customers.models import Address
from .models import PaymentMethod, Order, OrderItem

# Create your tests here.


class OrderModelTest(TestCase):
    
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        
        # Create a test address
        self.address = Address.objects.create(
            user=self.user,
            street="123 Test St",
            city="Test City",
            country="Test Country",
            postal_code="12345"
        )
        
        # Create a test payment method
        self.payment_method = PaymentMethod.objects.create(name="credit_card", description="Test credit card payment")
        
        # Create a test product
        self.product = Product.objects.create(
            name="Test Product",
            price=100.00,
            category=None  # You can set a category or mock one
        )
        
        # Create an order and add items to it
        self.order = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            payment_method=self.payment_method
        )
        
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

    def test_order_creation(self):
        """Test that an order is created with the correct fields."""
        self.assertEqual(self.order.user, self.user)
        self.assertEqual(self.order.shipping_address, self.address)
        self.assertEqual(self.order.status, Order.Status.PENDING)
        self.assertEqual(self.order.payment_method, self.payment_method)
        self.assertEqual(self.order.order_number, 1)  # Assuming it's the first order

    def test_order_item_creation(self):
        """Test that an order item is created with correct price and quantity."""
        self.assertEqual(self.order_item.product, self.product)
        self.assertEqual(self.order_item.quantity, 2)
        self.assertEqual(self.order_item.price, self.product.price)
        self.assertEqual(self.order_item.total_price(), self.product.price * 2)

    def test_order_total_price(self):
        """Test that the total price method sums up all order items."""
        # Create another item for the same order to test total price calculation
        another_product = Product.objects.create(name="Another Product", price=50.00, category=None)
        another_order_item = OrderItem.objects.create(
            order=self.order,
            product=another_product,
            quantity=1,
            price=another_product.price
        )
        self.assertEqual(self.order.total_price(), (self.product.price * 2) + (another_product.price * 1))

    def test_order_save_order_number(self):
        """Test that order number is auto-generated correctly."""
        order2 = Order.objects.create(
            user=self.user,
            shipping_address=self.address,
            payment_method=self.payment_method
        )
        self.assertEqual(order2.order_number, 2)

    def test_order_status_choices(self):
        """Test that the status choices are valid."""
        self.assertEqual(Order.Status.PENDING, 'Pending')
        self.assertEqual(Order.Status.COMPLETED, 'Completed')
        self.assertEqual(Order.Status.CANCELED, 'Canceled')
        self.assertEqual(Order.Status.SHIPPED, 'Shipped')

    def test_payment_method_creation(self):
        """Test the creation of payment method."""
        payment_method = PaymentMethod.objects.create(name="paypal", description="Test PayPal payment")
        self.assertEqual(payment_method.name, "paypal")
        self.assertEqual(payment_method.description, "Test PayPal payment")

    def test_order_item_price_from_product_discount(self):
        """Test that the price is correctly set from product's discounted price."""
        self.product.discount = None  # No discount
        self.product.save()

        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
            price=self.product.get_price_after_discount()  # Should pick the normal price
        )
        self.assertEqual(order_item.price, self.product.price)
        
        # Now, apply a discount to the product
        self.product.discount = Discount.objects.create(discount_type="percentage", value=10, start_date=timezone.now(), end_date=timezone.now() + timedelta(days=1))
        self.product.save()
        order_item.price = self.product.get_price_after_discount()
        order_item.save()
        
        self.assertEqual(order_item.price, self.product.price * 0.9)  # Expecting 10% discount applied

    def test_order_item_product_description(self):
        """Test that the product description is properly saved in OrderItem."""
        self.order_item.product_description = "A detailed description of the product"
        self.order_item.save()
        self.assertEqual(self.order_item.product_description, "A detailed description of the product")

