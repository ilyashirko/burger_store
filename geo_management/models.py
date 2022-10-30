from django.db import models
from django.conf import settings
import requests


class LocationQuerySet(models.QuerySet):
    def get_or_create(self, defaults=None, **kwargs):
        self._for_write = True
        try:
            return super().get(**kwargs), False
        except Location.DoesNotExist:
            kwargs['longitude'], kwargs['latitude'] = self._fetch_coordinates(kwargs['address'])
            return super().get_or_create(defaults, **kwargs)

    def _fetch_coordinates(self, address, apikey=settings.YA_GEO_API_KEY):
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return None, None

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return lon, lat


class Location(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        unique=True
    )
    longitude = models.FloatField('Долгота', max_length=15, null=True)
    latitude = models.FloatField('Широта', max_length=15, null=True)
    request_date = models.DateTimeField('Дата запроса', auto_now=True)
    objects = LocationQuerySet.as_manager()

    def is_corrupted(self):
        return self.longitude is None or self.longitude is None
