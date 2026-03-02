"""
Observer Pattern implementation via Django signals.

When a Room's `is_available` field changes, all subscribed users (observers)
are notified by creating a NotificationLog entry.
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Room, Subscription, NotificationLog


@receiver(pre_save, sender=Room)
def room_pre_save(sender, instance, **kwargs):
    """Capture the previous is_available value on the instance before saving."""
    if instance.pk:
        try:
            old = Room.objects.get(pk=instance.pk)
            instance._previous_is_available = old.is_available
        except Room.DoesNotExist:
            instance._previous_is_available = None
    else:
        instance._previous_is_available = None


@receiver(post_save, sender=Room)
def room_post_save(sender, instance, created, **kwargs):
    """
    After saving a room, check if availability changed.
    If yes, notify all subscribed observers by creating NotificationLog entries.
    """
    if created:
        return

    prev = getattr(instance, '_previous_is_available', None)
    if prev is None or prev == instance.is_available:
        return  # No change – do nothing

    # Availability changed → notify all subscribers (observers)
    status_text = "доступний" if instance.is_available else "недоступний"
    message = (
        f'Шановний підписнику! Статус номера «{instance.title}» змінився: '
        f'тепер він {status_text}.'
    )

    subscriptions = Subscription.objects.filter(room=instance).select_related('user')
    logs = [
        NotificationLog(
            subscription=sub,
            message=message,
            is_available=instance.is_available,
        )
        for sub in subscriptions
    ]
    if logs:
        NotificationLog.objects.bulk_create(logs)
