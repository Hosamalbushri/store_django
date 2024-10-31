# Generated by Django 4.2.11 on 2024-10-31 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0012_alter_product_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='status',
            field=models.CharField(choices=[('1', 'On'), ('0', 'Off')], default='1', max_length=1),
        ),
    ]
