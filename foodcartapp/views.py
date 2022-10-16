import json
from statistics import quantiles
from unittest.loader import VALID_MODULE_NAME
from urllib.error import HTTPError
from django.http import JsonResponse, HttpResponseBadRequest
from django.templatetags.static import static
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError

from foodcartapp.test import TEST_DATA
from .models import Order, OrderedProduct, Product
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import Serializer, CharField, ListField, ModelSerializer, IntegerField
from phonenumber_field.serializerfields import PhoneNumberField

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
            if value in available_products_ids:
                raise ValidationError('Product is not available')
            return value

    products = ListField(child=OrderProductSerializer(), allow_empty=False, write_only=True)
    firstname = CharField()
    lastname = CharField()
    phonenumber = PhoneNumberField()
    address = CharField()


# def check_order_data_validity(order_data):
#     order_keys = ('products', 'firstname', 'lastname', 'phonenumber', 'address')
#     for key in order_keys:
#         if key not in order_data or not order_data[key]:
#             raise ValidationError(f'There is no {key} in order')
#         if key != 'products' and not isinstance(order_data[key], str):
#             raise ValidationError(f'{key} must be string.')
#         elif key != 'products' and not isinstance(order_data['products'], (list, tuple)):
#             raise ValidationError('Products must be list or tuple.')
#     validate_international_phonenumber(order_data['phonenumber'])

# only fr development
def check_validator(test_data=TEST_DATA):
    from rest_framework.exceptions import ValidationError as drfValidationError
    for data in test_data:
        check = OrderSerializer(data=data)
        try:
            assert check.is_valid(raise_exception=True) is False
        except drfValidationError:
            pass
        except AssertionError:
            print(data)
            print(check.is_valid())
            input('ASSERTION ERROR')
    print('Validation with test data passed')


@api_view(['POST'])
def register_order(request):
    # only for development
    print('REGISTER_ORDER')
    check_validator()

    check = OrderSerializer(data=request.data)
    check.is_valid(raise_exception=True)
    
    order_object = Order.objects.create(
        first_name=request.data['firstname'],
        last_name=request.data['lastname'],
        phonenumber=request.data['phonenumber'],
        address=request.data['address']
    )
    for product in request.data['products']:
        ordered_product_object, _ = OrderedProduct.objects.get_or_create(
            product=Product.objects.get(id=product['product']),
            quantity=product['quantity']
        )
        order_object.products.add(ordered_product_object)
    order_object.save()
    
    return Response(request.data)
