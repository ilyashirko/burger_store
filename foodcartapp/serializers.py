from django.core.exceptions import ValidationError
from django.db import transaction
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.serializers import (CharField, IntegerField, ListField,
                                        Serializer)

from geo_management.processing import get_or_create_location

from .models import Order, OrderedProduct, Product


class OrderProductSerializer(Serializer):
        product = IntegerField()
        quantity = IntegerField(min_value=1)

        def validate_product(self, value):
            available_products_ids = [
                product.id
                for product
                in Product.objects.all().available()
            ]
            if value not in available_products_ids:
                raise ValidationError('Product is not available')
            return value


class OrderSerializer(Serializer):
    uuid = CharField(required=False)
    products = ListField(
        child=OrderProductSerializer(),
        allow_empty=False,
        write_only=True
    )
    firstname = CharField()
    lastname = CharField()
    phonenumber = PhoneNumberField()
    address = CharField()

    @transaction.atomic
    def create(self, validated_data):
        if not validated_data['products']:
            raise ValueError

        order_object = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )

        get_or_create_location(order_object.address)

        for product in validated_data['products']:
            product_object = Product.objects.get(id=product['product'])
            OrderedProduct.objects.get_or_create(
                order=order_object,
                product=product_object,
                quantity=product['quantity'],
                price_at_the_order_moment=product_object.price
            )
        self.uuid = order_object.uuid
        return order_object
