from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from io import StringIO

from hotel.models import Room, RoomCategory, Amenity


class SeedRoomsCommandTest(TestCase):
    """Тест management command seed_rooms"""

    def test_seed_creates_rooms(self):
        out = StringIO()
        call_command('seed_rooms', stdout=out)
        self.assertEqual(Room.objects.count(), 5)

    def test_seed_creates_categories(self):
        call_command('seed_rooms', stdout=StringIO())
        categories = list(RoomCategory.objects.values_list('name', flat=True))
        for name in ['Стандарт', 'Люкс', 'Сюїт', 'Апартаменти']:
            self.assertIn(name, categories)

    def test_seed_creates_amenities(self):
        call_command('seed_rooms', stdout=StringIO())
        self.assertGreaterEqual(Amenity.objects.count(), 1)

    def test_seed_is_idempotent(self):
        """Повторний запуск не дублює номери"""
        call_command('seed_rooms', stdout=StringIO())
        call_command('seed_rooms', stdout=StringIO())
        self.assertEqual(Room.objects.count(), 5)

    def test_seed_reset_flag(self):
        """--reset очищає і пересіює"""
        call_command('seed_rooms', stdout=StringIO())
        call_command('seed_rooms', '--reset', stdout=StringIO())
        self.assertEqual(Room.objects.count(), 5)

    def test_rooms_have_amenities(self):
        call_command('seed_rooms', stdout=StringIO())
        for room in Room.objects.all():
            self.assertGreater(room.amenities.count(), 0, f'{room.title} has no amenities')

    def test_rooms_have_category(self):
        call_command('seed_rooms', stdout=StringIO())
        for room in Room.objects.all():
            self.assertIsNotNone(room.category)

    def test_rooms_have_price(self):
        call_command('seed_rooms', stdout=StringIO())
        for room in Room.objects.all():
            self.assertGreater(room.price, 0)

class RoomListViewTest(TestCase):
    """Тест сторінки каталогу"""

    def setUp(self):
        call_command('seed_rooms', stdout=StringIO())
        self.client = Client()

    def test_room_list_status_200(self):
        response = self.client.get(reverse('room_list'))
        self.assertEqual(response.status_code, 200)

    def test_room_list_contains_rooms(self):
        response = self.client.get(reverse('room_list'))
        self.assertEqual(response.context['total'], 5)

    def test_filter_by_category(self):
        cat = RoomCategory.objects.get(name='Стандарт')
        response = self.client.get(reverse('room_list'), {'category': cat.id})
        for room in response.context['rooms']:
            self.assertEqual(room.category.name, 'Стандарт')

    def test_filter_by_availability(self):
        response = self.client.get(reverse('room_list'), {'available': 'on'})
        for room in response.context['rooms']:
            self.assertTrue(room.is_available)

    def test_filter_by_price_range(self):
        response = self.client.get(reverse('room_list'), {'price_min': 1000, 'price_max': 3000})
        for room in response.context['rooms']:
            self.assertGreaterEqual(room.price, 1000)
            self.assertLessEqual(room.price, 3000)

    def test_filter_by_capacity(self):
        response = self.client.get(reverse('room_list'), {'capacity': 2})
        for room in response.context['rooms']:
            self.assertEqual(room.capacity, 2)

    def test_search_filter(self):
        response = self.client.get(reverse('room_list'), {'search': 'Люкс'})
        for room in response.context['rooms']:
            self.assertIn('Люкс', room.title)

    def test_sort_price_asc(self):
        response = self.client.get(reverse('room_list'), {'sort': 'price-asc'})
        prices = [room.price for room in response.context['rooms']]
        self.assertEqual(prices, sorted(prices))

    def test_sort_price_desc(self):
        response = self.client.get(reverse('room_list'), {'sort': 'price-desc'})
        prices = [room.price for room in response.context['rooms']]
        self.assertEqual(prices, sorted(prices, reverse=True))

class RoomDetailViewTest(TestCase):
    """Тест сторінки деталей номера"""

    def setUp(self):
        call_command('seed_rooms', stdout=StringIO())
        self.client = Client()
        self.room = Room.objects.first()

    def test_room_detail_status_200(self):
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertEqual(response.status_code, 200)

    def test_room_detail_context(self):
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertEqual(response.context['room'], self.room)

    def test_room_detail_404(self):
        response = self.client.get(reverse('room_detail', args=[99999]))
        self.assertEqual(response.status_code, 404)