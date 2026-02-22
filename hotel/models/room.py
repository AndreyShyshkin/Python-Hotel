from django.db import models
from .room_category import RoomCategory
from .amenity import Amenity

class Room(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва або номер")
    description = models.TextField(verbose_name="Опис")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна за ніч")
    capacity = models.IntegerField(verbose_name="Місткість")
    image = models.ImageField(upload_to='rooms_images/', verbose_name="Фотографія")
    is_available = models.BooleanField(default=True, verbose_name="Доступно для бронювання")
    
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE, related_name='rooms', verbose_name="Категорія")
    amenities = models.ManyToManyField(Amenity, related_name='rooms', verbose_name="Зручності")

    class Meta:
        app_label = 'hotel'

    def __str__(self):
        return self.title