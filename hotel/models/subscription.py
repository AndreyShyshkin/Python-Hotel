from django.db import models
from django.contrib.auth.models import User
from .room import Room


class Subscription(models.Model):
    """Observer pattern: a user subscribes to availability changes of a room."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name="Користувач",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name="Номер",
    )
    email = models.EmailField(verbose_name="Email для сповіщень")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата підписки")

    class Meta:
        app_label = 'hotel'
        unique_together = ('user', 'room')
        verbose_name = "Підписка"
        verbose_name_plural = "Підписки"

    def __str__(self):
        return f"{self.user.username} → {self.room.title}"


class NotificationLog(models.Model):
    """Log of observer notifications sent to subscribers."""
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name="Підписка",
    )
    message = models.TextField(verbose_name="Повідомлення")
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name="Час відправки")
    is_available = models.BooleanField(verbose_name="Статус доступності")

    class Meta:
        app_label = 'hotel'
        verbose_name = "Лог сповіщення"
        verbose_name_plural = "Логи сповіщень"
        ordering = ['-sent_at']

    def __str__(self):
        return f"[{self.sent_at:%d.%m.%Y %H:%M}] {self.subscription}"
