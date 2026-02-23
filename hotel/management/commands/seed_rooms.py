"""
Management command: seed_rooms
Usage:
    python manage.py seed_rooms          # create 5 rooms (skip if already exist)
    python manage.py seed_rooms --reset  # wipe all rooms/categories/amenities first
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from hotel.models import Amenity, Room, RoomCategory

# ── static images that already live in the project ──────────────────────────
STATIC_IMAGES_DIR = Path(settings.BASE_DIR) / 'static' / 'images'

ROOMS_DATA = [
    {
        'title': 'Стандартний номер',
        'description': (
            'Затишний стандартний номер площею 25 м², оформлений у теплих тонах. '
            'Оснащений двоспальним ліжком преміум-класу, робочим столом, '
            'плазмовим телевізором та власною ванною кімнатою з душовою кабіною. '
            'Ідеально підходить для ділових поїздок та короткого відпочинку.'
        ),
        'price': '1500.00',
        'capacity': 2,
        'is_available': True,
        'category': 'Стандарт',
        'image_src': 'room1.jpg',
        'amenities': ['WiFi', 'Ресторан', 'Парковка'],
    },
    {
        'title': 'Люкс Преміум',
        'description': (
            'Розкішний номер люкс площею 50 м² з панорамним видом на місто. '
            'Включає окрему вітальню, кінгсайз-ліжко з постіллю єгипетської бавовни, '
            'мармурову ванну кімнату з джакузі, міні-бар та приватний балкон. '
            'Для гостей, що цінують найвищий рівень комфорту.'
        ),
        'price': '4500.00',
        'capacity': 2,
        'is_available': True,
        'category': 'Люкс',
        'image_src': 'room2.jpg',
        'amenities': ['WiFi', 'Басейн', 'Спа', 'Ресторан', 'Тренажерний зал'],
    },
    {
        'title': 'Сімейний сюїт',
        'description': (
            'Просторий сімейний сюїт площею 75 м² з двома окремими спальнями '
            'та великою загальною вітальнею. Перша спальня оснащена кінгсайз-ліжком, '
            'друга — двома односпальними ліжками. Дитячий куточок, велика ванна кімната '
            'та повністю обладнана кухня роблять цей номер ідеальним для сімей з дітьми.'
        ),
        'price': '6800.00',
        'capacity': 4,
        'is_available': True,
        'category': 'Сюїт',
        'image_src': 'room3.jpg',
        'amenities': ['WiFi', 'Ресторан', 'Тренажерний зал', 'Вітальня', 'Парковка'],
    },
    {
        'title': 'Президентські апартаменти',
        'description': (
            'Найпрестижніший номер готелю площею 120 м² на верхньому поверсі. '
            'Приватна тераса з панорамним видом, власний кінотеатр, більярдна кімната, '
            'дизайнерські меблі ручної роботи та цілодобовий персональний дворецький. '
            'Джакузі на відкритому повітрі та преміальний міні-бар включені у вартість.'
        ),
        'price': '12000.00',
        'capacity': 4,
        'is_available': False,
        'category': 'Апартаменти',
        'image_src': 'item1.jpg',
        'amenities': ['WiFi', 'Басейн', 'Спа', 'Ресторан', 'Тренажерний зал', 'Вітальня'],
    },
    {
        'title': 'Стандарт Делюкс',
        'description': (
            'Покращена версія стандартного номера площею 35 м². '
            'Оформлений у сучасному мінімалістичному стилі з використанням '
            'натуральних матеріалів. Велике ліжко з ортопедичним матрацом, '
            'смарт-телевізор, кавова машина Nespresso та панорамне вікно з '
            'видом на сад роблять перебування особливо приємним.'
        ),
        'price': '2200.00',
        'capacity': 1,
        'is_available': True,
        'category': 'Стандарт',
        'image_src': 'item2.jpg',
        'amenities': ['WiFi', 'Ресторан', 'Парковка'],
    },
]

ALL_AMENITIES = [
    'WiFi', 'Басейн', 'Спа', 'Ресторан',
    'Тренажерний зал', 'Вітальня', 'Парковка',
]

ALL_CATEGORIES = ['Стандарт', 'Люкс', 'Сюїт', 'Апартаменти']


class Command(BaseCommand):
    help = 'Seed the database with 5 sample hotel rooms'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing rooms, categories and amenities before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            Room.objects.all().delete()
            RoomCategory.objects.all().delete()
            Amenity.objects.all().delete()
            self.stdout.write(self.style.WARNING('🗑  Existing data wiped.'))

        # ── ensure media directory exists ──────────────────────────────────
        media_dir = Path(settings.MEDIA_ROOT) / 'rooms_images'
        media_dir.mkdir(parents=True, exist_ok=True)

        # ── create amenities ───────────────────────────────────────────────
        amenity_objs = {}
        for name in ALL_AMENITIES:
            obj, created = Amenity.objects.get_or_create(name=name)
            amenity_objs[name] = obj
            if created:
                self.stdout.write(f'  ✅ Amenity: {name}')

        # ── create categories ──────────────────────────────────────────────
        category_objs = {}
        for name in ALL_CATEGORIES:
            obj, created = RoomCategory.objects.get_or_create(name=name)
            category_objs[name] = obj
            if created:
                self.stdout.write(f'  ✅ Category: {name}')

        # ── create rooms ───────────────────────────────────────────────────
        created_count = 0
        for data in ROOMS_DATA:
            if Room.objects.filter(title=data['title']).exists():
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Skipped (already exists): {data["title"]}')
                )
                continue

            # copy static image → media/rooms_images/
            src = STATIC_IMAGES_DIR / data['image_src']
            dest_filename = f'seed_{data["image_src"]}'
            dest = media_dir / dest_filename

            if src.exists():
                shutil.copy2(src, dest)
                image_field_value = f'rooms_images/{dest_filename}'
            else:
                self.stdout.write(
                    self.style.WARNING(f'    ⚠️  Image not found: {src}, leaving blank')
                )
                image_field_value = ''

            room = Room.objects.create(
                title=data['title'],
                description=data['description'],
                price=data['price'],
                capacity=data['capacity'],
                is_available=data['is_available'],
                category=category_objs[data['category']],
                image=image_field_value,
            )
            room.amenities.set([amenity_objs[a] for a in data['amenities']])
            created_count += 1
            status = '🟢 available' if data['is_available'] else '🔴 occupied'
            self.stdout.write(
                self.style.SUCCESS(
                    f'  🛏  Created: {room.title} | {room.price} ₴ | {status}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ Done! {created_count} room(s) created, '
                f'{len(ROOMS_DATA) - created_count} skipped.'
            )
        )
