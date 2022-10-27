# Generated by Django 3.2.15 on 2022-10-27 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0048_auto_20221027_0837'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('N', 'Ожидает подтверждения'), ('A', 'Сборка'), ('D', 'Доставляется'), ('C', 'Выполнен')], default='N', max_length=50, verbose_name='Статус заказа'),
        ),
    ]