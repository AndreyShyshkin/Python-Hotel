from django.db import models

class Amenity(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва зручності")

    class Meta:
        app_label = 'hotel'

    def __str__(self):
        return self.name