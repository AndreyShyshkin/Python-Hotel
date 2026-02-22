from django.contrib import admin
from .models.room import Room
from .models.room_category import RoomCategory
from .models.amenity import Amenity

@admin.register(RoomCategory)
class RoomCategoryAdmin(admin.ModelAdmin):
    pass

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    pass

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'description')