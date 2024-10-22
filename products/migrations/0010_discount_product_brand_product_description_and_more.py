# Generated by Django 4.2.11 on 2024-10-18 22:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_brand'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_type', models.CharField(choices=[('percentage', 'Percentage'), ('fixed', 'Fixed Amount')], max_length=10)),
                ('value', models.DecimalField(decimal_places=2, max_digits=5)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.brand'),
        ),
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, default='2000', max_digits=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='discount',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.discount'),
        ),
    ]