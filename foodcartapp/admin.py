from django.contrib import admin
from django.shortcuts import redirect, reverse
from django.templatetags.static import static
from django.utils.html import format_html

from geo_management.processing import get_or_create_location

from .models import (Order, OrderedProduct, Product, ProductCategory,
                     Restaurant, RestaurantMenuItem)


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]

    def save_model(self, request, obj, form, change):
        if 'address' in form.changed_data:
            get_or_create_location(form.data['address'])
        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly, so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>',
            url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url,
            src=obj.image.url
        )
    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategory(admin.ModelAdmin):
    pass


class OrderedProductInline(admin.TabularInline):
    model = OrderedProduct
    readonly_fields = ('price_at_the_order_moment', )
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'firstname',
        'lastname',
        'phonenumber',
        'created_at',
        'status',
    )
    readonly_fields = ['created_at', ]
    inlines = (OrderedProductInline, )
    ordering = ('-status', 'created_at', )

    def save_model(self, request, obj, form, change):
        if 'address' in form.changed_data:
            get_or_create_location(form.data['address'])
        if 'executor' in form.changed_data and form.data['executor']:
            obj.status = 'in_process'
        elif 'executor' in form.changed_data and not form.data['executor']:
            obj.status = 'new'
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        added_products = formset.save(commit=False)
        deleted_products = formset.deleted_objects
        for ordered_product in deleted_products:
            ordered_product.delete()
        for ordered_product in added_products:
            if not ordered_product.price_at_the_order_moment:
                current_price = ordered_product.product.price
                ordered_product.price_at_the_order_moment = current_price
            ordered_product.save()

    def response_change(self, request, obj):
        response = super().response_change(request, obj)
        if "return" in request.GET:
            return redirect(request.GET['return'])
        else:
            return response


@admin.register(OrderedProduct)
class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity')
    readonly_fields = ('price_at_the_order_moment', )
