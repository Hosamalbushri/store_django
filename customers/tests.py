
# Create your tests here.
from django.test import TestCase
from django.contrib.auth import get_user_model
from products.models import Product
from .models import Customer, Address, Favorite, Cart, CartItem

class CustomerModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.customer = Customer.objects.create(user=self.user, phone_number="1234567890", gender="M")
    
    def test_customer_creation(self):
        """Test that a customer is created correctly."""
        self.assertEqual(self.customer.user.username, "testuser")
        self.assertEqual(self.customer.phone_number, "1234567890")
        self.assertEqual(self.customer.gender, "M")
        self.assertEqual(str(self.customer), self.customer.user.username)


class AddressModelTest(TestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.address = Address.objects.create(
            user=self.user,
            name="John Doe",
            email="john@example.com",
            phone_number="1234567890",
            country="Test Country",
            city="Test City",
            street="123 Test St",
            postal_code="12345",
            is_default=True
        )

    def test_address_creation(self):
        """Test that an address is created and fields are correctly capitalized."""
        self.assertEqual(self.address.name, "John Doe")
        self.assertEqual(self.address.street, "123 Test St")
        self.assertEqual(self.address.city, "Test City")
        self.assertEqual(self.address.country, "Test Country")
        self.assertEqual(self.address.postal_code, "12345")
        self.assertTrue(self.address.is_default)
        self.assertEqual(str(self.address), "John Doe, 123 Test St, Test City,Test Country - 12345")


class FavoriteModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.product = Product.objects.create(name="Test Product", price=100.00)
        self.favorite = Favorite.objects.create(user=self.user, product=self.product)

    def test_favorite_creation(self):
        """Test that a favorite is correctly created."""
        self.assertEqual(self.favorite.user.username, "testuser")
        self.assertEqual(self.favorite.product.name, "Test Product")
        self.assertEqual(str(self.favorite), f"{self.favorite.user.username} - {self.favorite.product.name}")
    
    def test_unique_favorite(self):
        """Test that a user cannot favorite the same product twice."""
        with self.assertRaises(Exception):
            Favorite.objects.create(user=self.user, product=self.product)


class CartModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_creation(self):
        """Test that a cart is correctly created."""
        self.assertEqual(self.cart.user.username, "testuser")
        self.assertEqual(str(self.cart), f"Cart for {self.cart.user.username}")
    
    def test_cart_total_price(self):
        """Test that the total price calculation is correct."""
        product1 = Product.objects.create(name="Test Product 1", price=100.00)
        product2 = Product.objects.create(name="Test Product 2", price=150.00)
        
        cart_item1 = CartItem.objects.create(cart=self.cart, product=product1, quantity=2)
        cart_item2 = CartItem.objects.create(cart=self.cart, product=product2, quantity=1)
        
        self.assertEqual(self.cart.total_price(), (product1.price * 2) + (product2.price * 1))


class CartItemModelTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username="testuser", password="password")
        self.cart = Cart.objects.create(user=self.user)
        self.product = Product.objects.create(name="Test Product", price=100.00)
        self.cart_item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_cart_item_creation(self):
        """Test that a cart item is created correctly."""
        self.assertEqual(self.cart_item.product.name, "Test Product")
        self.assertEqual(self.cart_item.quantity, 2)
        self.assertEqual(str(self.cart_item), f"{self.cart_item.quantity} of {self.cart_item.product.name} in cart")

    def test_cart_item_total_price(self):
        """Test that the total price of the cart item is correct."""
        discounted_price = self.product.get_price_after_discount()  # Assuming no discount for this example
        self.assertEqual(self.cart_item.total_price(), discounted_price * 2)
