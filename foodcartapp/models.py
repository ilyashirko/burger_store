from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Sum
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class OrderQuerySet(models.QuerySet):
    def actual_orders(self):
        return self.exclude(status='complete') \
            .order_by('-status', 'created_at')

    def with_products(self):
        return self.prefetch_related('ordered_products__product')

    def with_total(self):
        return self.annotate(
            total=Sum(
                F('ordered_products__price_at_the_order_moment') *
                F('ordered_products__quantity')
                )
            )


class Order(models.Model):
    STATUSES = (
        ('new', 'Ожидает подтверждения'),
        ('in_process', 'Готовится'),
        ('assembly', 'Сборка'),
        ('delivery', 'Доставляется'),
        ('complete', 'Выполнен')
    )

    PAYMENT_METHODS = (
        ('online', 'Онлайн, безнал'),
        ('upon_delivery', 'На адресе, наличные'),
        ('clarify', 'Уточнить у клиента')
    )

    firstname = models.CharField('Имя заказчика', max_length=100)
    lastname = models.CharField('Фамилия заказчика', max_length=100)
    phonenumber = PhoneNumberField('Телефон заказчика')
    address = models.CharField('Адрес заказчика', max_length=200)
    created_at = models.DateTimeField(
        "Сформирован",
        auto_now_add=True
    )
    called_at = models.DateTimeField(
        "Время звонка",
        blank=True,
        null=True,
    )
    delivered_at = models.DateTimeField(
        "Доставлен",
        blank=True,
        null=True,
    )
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField(
        'Статус заказа',
        max_length=50,
        choices=STATUSES,
        default='new'
    )
    payment_method = models.CharField(
        'Способ оплаты',
        max_length=50,
        choices=PAYMENT_METHODS,
        default='clarify'
    )
    executor = models.ForeignKey(
        'Restaurant',
        verbose_name='Исполнитель',
        related_name='orders',
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )
    objects = OrderQuerySet.as_manager()

    def __str__(self):
        return (
            f'[{self.id}] - {self.phonenumber} '
            f'({self.firstname} {self.lastname})'
        )

    class Meta:
        indexes = [
            models.Index(fields=['phonenumber']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['called_at']),
            models.Index(fields=['delivered_at']),
        ]


class OrderedProduct(models.Model):
    order = models.ForeignKey(
        'Order',
        verbose_name='Заказ',
        related_name='ordered_products',
        on_delete=models.PROTECT
    )
    product = models.ForeignKey(
        'Product',
        verbose_name='Товар',
        related_name='ordered_products',
        on_delete=models.PROTECT,
    )
    quantity = models.SmallIntegerField(
        'Количество',
        validators=[MinValueValidator(1)],
    )
    price_at_the_order_moment = models.DecimalField(
        'Цена на время заказа',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return self.product.name

    def get_summ(self):
        return self.price_at_the_order_moment * self.quantity
