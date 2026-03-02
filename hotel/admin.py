from django.contrib import admin
from .models import Room, RoomCategory, Amenity, Subscription, NotificationLog

admin.site.register(RoomCategory)
admin.site.register(Amenity)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'capacity', 'category', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('title', 'description')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'email', 'created_at')
    list_filter = ('room', 'room__category')
    search_fields = ('user__username', 'user__email', 'room__title', 'email')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('sent_at', 'get_user', 'get_room', 'is_available', 'short_message')
    list_filter = ('is_available', 'subscription__room', 'sent_at')
    search_fields = ('subscription__user__username', 'subscription__room__title', 'message')
    readonly_fields = ('subscription', 'message', 'sent_at', 'is_available')
    date_hierarchy = 'sent_at'

    @admin.display(description='Користувач', ordering='subscription__user__username')
    def get_user(self, obj):
        return obj.subscription.user.username

    @admin.display(description='Номер', ordering='subscription__room__title')
    def get_room(self, obj):
        return obj.subscription.room.title

    @admin.display(description='Повідомлення')
    def short_message(self, obj):
        return obj.message[:80] + ('…' if len(obj.message) > 80 else '')

