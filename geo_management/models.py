from django.db import models


class Location(models.Model):
    address = models.CharField(
        'Адрес',
        max_length=100,
        unique=True
    )
    longitude = models.FloatField('Долгота', max_length=15, null=True)
    latitude = models.FloatField('Широта', max_length=15, null=True)
    request_date = models.DateTimeField('Дата запроса', auto_now=True)

    def is_corrupted(self):
        return self.longitude is None or self.longitude is None
