# Generated by Django 3.2.15 on 2022-11-03 10:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0067_alter_orderedproduct_price_at_the_order_moment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderedproduct',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordered_product', to='foodcartapp.order', verbose_name='Заказ'),
        ),
    ]
