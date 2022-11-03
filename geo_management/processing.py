import requests
from django.conf import settings

from .models import Location


def fetch_coordinates(address, apikey=settings.YA_GEO_API_KEY):
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


def get_or_create_location(address):
    try:
        return Location.objects.get(address=address)
    except Location.DoesNotExist:
        longitude, latitude = fetch_coordinates(address)
        return Location.objects.create(
            address=address,
            longitude=longitude,
            latitude=latitude
        )
