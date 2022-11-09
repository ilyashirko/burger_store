# Generated by Django 3.2.15 on 2022-10-14 10:00

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0037_auto_20210125_1833'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderedProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.SmallIntegerField(verbose_name='Количество')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ordered_product', to='foodcartapp.product', verbose_name='Товар')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100, verbose_name='Имя заказчика')),
                ('last_name', models.CharField(max_length=100, verbose_name='Фамилия заказчика')),
                ('phonenumber', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, verbose_name='Телефон заказчика')),
                ('address', models.CharField(max_length=200, verbose_name='Адрес заказчика')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Сформирован')),
                ('is_actual', models.BooleanField(verbose_name='Заказ в работе')),
                ('products', models.ManyToManyField(related_name='orders', to='foodcartapp.OrderedProduct', verbose_name='Товары')),
            ],
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['phonenumber'], name='foodcartapp_phonenu_5f4ceb_idx'),
        ),
    ]
