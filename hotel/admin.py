from django.contrib import admin
from .models import Room, RoomCategory, Amenity
admin.site.register(RoomCategory)
admin.site.register(Amenity)
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'capacity', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'description')