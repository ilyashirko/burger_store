from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from geo_management.processing import get_or_create_location

from .models import Order, OrderedProduct, Product


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = ["product", "quantity"]


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(
        many=True,
        allow_empty=False,
        source='ordered_products'
    )
    
    class Meta:
        model = Order
        fields = [
            "firstname",
            "lastname",
            "phonenumber",
            "address",
            "products",
        ]

    def create(self, validated_data):
        if not validated_data['ordered_products']:
            raise ValidationError
        order_object = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address']
        )
        get_or_create_location(order_object.address)
        for product in validated_data['ordered_products']:
            product_object = Product.objects.get(id=product['product'].id)
            OrderedProduct.objects.get_or_create(
                order=order_object,
                product=product_object,
                quantity=product['quantity'],
                price_at_the_order_moment=product_object.price
            )
        self.id = order_object.id
        return order_object
