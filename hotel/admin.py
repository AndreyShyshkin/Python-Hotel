from django.contrib import admin
from .models import RoomCategory, Amenity, Room

admin.site.register(RoomCategory)
admin.site.register(Amenity)
admin.site.register(Room)