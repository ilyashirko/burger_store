import json
from urllib.error import HTTPError
from django.http import JsonResponse, HttpResponseBadRequest
from django.templatetags.static import static
from phonenumber_field.validators import validate_international_phonenumber
from django.core.exceptions import ValidationError
from .models import Order, OrderedProduct, Product
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
            'text': 'Food is incomplete without a tasty dessert',
        }
    ]
    )
    

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


def check_order_data_validity(order_data):
    order_keys = ('products', 'firstname', 'lastname', 'phonenumber', 'address')
    for key in order_keys:
        if key not in order_data or not order_data[key]:
            raise ValidationError(f'There is no {key} in order')
        if key != 'products' and not isinstance(order_data[key], str):
            raise ValidationError(f'{key} must be string.')
        elif key != 'products' and not isinstance(order_data['products'], (list, tuple)):
            raise ValidationError('Products must be list or tuple.')
    validate_international_phonenumber(order_data['phonenumber'])


@api_view(['POST'])
def register_order(request):
    print('REGISTER_ORDER')

    try:
        check_order_data_validity(request.data)
    except ValidationError as error:
        print(error)
        return Response({'error': error})

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
