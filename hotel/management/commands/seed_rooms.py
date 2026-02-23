from django.core.management.base import BaseCommand
from django.core.management.base import BaseCommand
from hotel.models import Amenity, Room, RoomCategory

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
    help = 'Seed the database with sample hotel rooms'

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
            
        category_objs = {}
        for name in ALL_CATEGORIES:
            obj, _ = RoomCategory.objects.get_or_create(name=name)
            category_objs[name] = obj

        
        for data in ROOMS_DATA:
            if not Room.objects.filter(title=data['title']).exists():
                Room.objects.create(
                    title=data['title'],
                    description=data['description'],
                    price=data['price'],
                    capacity=data['capacity'],
                    is_available=data['is_available'],
                    category=category_objs[data['category']],
                    image='' 
                )
        self.stdout.write(self.style.SUCCESS('Rooms created successfully!'))
        
