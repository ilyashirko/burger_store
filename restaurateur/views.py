import os
import requests
from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from foodcartapp.models import Order, Product, Restaurant
from geopy.distance import distance as calc_distance
from geo_management.models import Location



class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {
            item.restaurant_id: item.availability
            for item in product.menu_items.all()
        }
        ordered_availability = [
            availability.get(restaurant.id, False)
            for restaurant in restaurants
        ]
        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_available_executors(order,
                            current_restaurants=Restaurant.objects.all()):
    ordered_products = set(
        ordered_product.product
        for ordered_product in order.ordered_product.all()
    )
    available_executors = list()
    for restaurant in current_restaurants:
        restaurant_products = set(
            item.product for item in restaurant.menu_items.all()
        )
        if ordered_products.issubset(restaurant_products):
            available_executors.append(restaurant)
    return available_executors


def get_restaurants_with_distance(restaurants_with_locations, order):

    order_coordinates, _ = Location.objects.get_or_create(address=order.address)
    available_restaurants = list()
    for restaurant in get_available_executors(order, restaurants_with_locations):
        if order_coordinates.is_corrupted() or restaurant.location.is_corrupted():
            distance = None
        else:
            distance = round(
                calc_distance(
                    (
                        order_coordinates.longitude,
                        order_coordinates.latitude
                    ),
                    (
                        restaurant.location.longitude,
                        restaurant.location.latitude
                    )
                ).km,
                1
            )
        available_restaurants.append(
            {
                'name': restaurant.name,
                'distance': distance
            }
        )
    return available_restaurants


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    actual_orders = Order.objects.actual_orders()
    restaurants = Restaurant.objects.prefetch_related('menu_items__product')

    for restaurant in restaurants:
        restaurant_location, _ = Location.objects.get_or_create(address=restaurant.address)
        restaurant.location = restaurant_location

    order_items = [
        {
            'uuid': order.uuid,
            'status': order.get_status_display(),
            'payment_method': order.get_payment_method_display(),
            'client': f'{order.firstname} {order.lastname}',
            'phonenumber': str(order.phonenumber),
            'address': order.address,
            'price': order.calc_price(),
            'comment': order.comment if order.comment else '',
            'available_restaurants': get_restaurants_with_distance(restaurants, order),
            'executor': order.executor if order.executor else None,
        }
        for order in actual_orders
    ]
 
    return render(request, template_name='order_items.html', context={
        'order_items': order_items,
        'return_url': request.path
    })
