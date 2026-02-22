from django.db import models

class Amenity(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва зручності")

    class Meta:
        app_label = 'hotel'
        verbose_name = "Зручність"
        verbose_name_plural = "Зручності"

    def __str__(self):
        return self.name