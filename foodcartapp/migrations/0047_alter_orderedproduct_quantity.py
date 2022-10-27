# Generated by Django 3.2.15 on 2022-10-27 08:29

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0046_alter_orderedproduct_price_at_the_order_moment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='quantity',
            field=models.SmallIntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Количество'),
        ),
    ]