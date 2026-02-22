from django.db import models

class RoomCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")

    class Meta:
        app_label = 'hotel'

    def __str__(self):
        return self.name