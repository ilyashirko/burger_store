# Generated by Django 3.2.15 on 2022-11-03 10:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0065_alter_orderedproduct_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='price_at_the_order_moment',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=8, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Цена на время заказа'),
            preserve_default=False,
        ),
    ]
