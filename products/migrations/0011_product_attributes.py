# Generated by Django 4.2.11 on 2024-10-18 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_discount_product_brand_product_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='attributes',
            field=models.ManyToManyField(blank=True, to='products.subattribute'),
        ),
    ]
