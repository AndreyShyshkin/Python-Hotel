import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Email для сповіщень')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата підписки')),
                ('room', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subscribers',
                    to='hotel.room',
                    verbose_name='Номер',
                )),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='subscriptions',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Користувач',
                )),
            ],
            options={
                'verbose_name': 'Підписка',
                'verbose_name_plural': 'Підписки',
                'unique_together': {('user', 'room')},
            },
        ),
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField(verbose_name='Повідомлення')),
                ('sent_at', models.DateTimeField(auto_now_add=True, verbose_name='Час відправки')),
                ('is_available', models.BooleanField(verbose_name='Статус доступності')),
                ('subscription', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to='hotel.subscription',
                    verbose_name='Підписка',
                )),
            ],
            options={
                'verbose_name': 'Лог сповіщення',
                'verbose_name_plural': 'Логи сповіщень',
                'ordering': ['-sent_at'],
            },
        ),
    ]
