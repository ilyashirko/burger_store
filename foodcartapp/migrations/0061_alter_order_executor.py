# Generated by Django 3.2.15 on 2022-10-30 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_alter_order_executor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='executor',
            field=models.CharField(blank=True, choices=[('[TEST] Бургер и точка', '[TEST] Бургер и точка'), ('[TEST] Бутер и точка', '[TEST] Бутер и точка'), ('[TEST] Мясо и точка', '[TEST] Мясо и точка')], max_length=50, verbose_name='Исполнитель'),
        ),
    ]
