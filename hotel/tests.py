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