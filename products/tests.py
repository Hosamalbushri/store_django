from django.test import TestCase
# myapp/tests.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Category, Attribute, SubAttribute, Brand, Discount, Product, ProductImage
from filer.models import Image
from datetime import timedelta


# Create your tests here.

class CategoryModelTest(TestCase):
    def setUp(self):
        self.parent_category = Category.objects.create(name="Electronics")
        self.child_category = Category.objects.create(name="Laptops", parent=self.parent_category)

    def test_category_hierarchy(self):
        self.assertEqual(self.child_category.parent, self.parent_category)
        self.assertEqual(str(self.child_category), "Electronics -> Laptops")

    def test_self_parent(self):
        self.parent_category.parent = self.parent_category
        with self.assertRaises(ValidationError):
            self.parent_category.clean()

    def test_circular_reference(self):
        self.parent_category.parent = self.child_category
        with self.assertRaises(ValidationError):
            self.parent_category.clean()

    def test_update_children_status(self):
        self.parent_category.status = '0'
        self.parent_category.save()
        self.child_category.refresh_from_db()
        self.assertEqual(self.child_category.status, '0')
    
    def test_delete_with_children(self):
        with self.assertRaises(ValidationError):
            self.parent_category.delete()



class AttributeModelTest(TestCase):
    def setUp(self):
        self.attribute = Attribute.objects.create(name="Color", attribute_type="text")
        self.sub_attribute = SubAttribute.objects.create(parent_attribute=self.attribute, name="Red", value="FF0000")

    def test_attribute_creation(self):
        self.assertEqual(self.attribute.name, "Color")
    
    def test_sub_attribute_creation(self):
        self.assertEqual(self.sub_attribute.parent_attribute, self.attribute)
        self.assertEqual(str(self.sub_attribute), "( Color )-->RED")
    
  



class BrandModelTest(TestCase):
    def setUp(self):
        self.brand = Brand.objects.create(name="Apple")

    def test_brand_creation(self):
        self.assertEqual(self.brand.name, "Apple")




class DiscountModelTest(TestCase):
    def setUp(self):
        self.discount = Discount.objects.create(
            discount_type="percentage",
            value=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
            active=True
        )

    def test_discount_creation(self):
        self.assertEqual(str(self.discount), "10% off")
    
    def test_end_date_after_start_date(self):
        self.discount.end_date = self.discount.start_date - timedelta(days=1)
        with self.assertRaises(ValidationError):
            self.discount.clean()

    def test_is_valid(self):
        self.assertTrue(self.discount.is_valid())



class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Electronics")
        self.discount = Discount.objects.create(
            discount_type="fixed",
            value=10,
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=1),
            active=True
        )
        self.product = Product.objects.create(
            name="Laptop",
            category=self.category,
            price=1000,
            discount=self.discount
        )

    def test_product_price_after_discount(self):
        self.assertEqual(self.product.get_price_after_discount(), 990)

    def test_product_name_formatting(self):
        self.product.name = "laptop pro"
        self.product.save()
        self.assertEqual(self.product.name, "Laptop Pro")





