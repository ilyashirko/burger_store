from django.core.exceptions import ValidationError
from django.db import transaction
from django.templatetags.static import static
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import (CharField, IntegerField, ListField,
                                        Serializer)

from .models import Order, OrderedProduct, Product
from geo_management.processing import get_or_create_location


@api_view(['GET'])
def banners_list_api(request):
    # FIXME move data to db?
    return Response(
        [
            {
                'title': 'Burger',
                'src': static('burger.jpg'),
                'text': 'Tasty Burger at your door step',
            },
            {
                'title': 'Spices',
                'src': static('food.jpg'),
                'text': 'All Cuisines',
            },
            {
                'title': 'New York',
                'src': static('tasty.jpg'),
                'text': 'Food is incomplete without a tachild',
            }
        ])


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return Response(dumped_products)


class OrderSerializer(Serializer):
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


@api_view(['POST'])
def register_order(request):
    check = OrderSerializer(data=request.data)
    check.is_valid(raise_exception=True)
    check.save()
    check.data['phonenumber'] = str(check.data['phonenumber'])
    return Response(check.data)
