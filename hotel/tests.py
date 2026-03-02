from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from django.contrib.auth.models import User
from io import StringIO

from hotel.models import Room, RoomCategory, Amenity, Subscription, NotificationLog


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

    def test_similar_rooms_same_category(self):
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        for r in response.context['similar_rooms']:
            self.assertEqual(r.category, self.room.category)
            self.assertNotEqual(r.pk, self.room.pk)


# ── Observer Pattern Tests ──────────────────────────────────────────────────

class ObserverSubscriptionTest(TestCase):
    """Тести патерну Спостерігач: підписки та логи сповіщень"""

    def setUp(self):
        call_command('seed_rooms', stdout=StringIO())
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='TestPass123!', email='test@hotel.com'
        )
        self.room = Room.objects.first()

    # -- Subscribe --

    def test_subscribe_creates_subscription(self):
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(
            reverse('subscribe_room', args=[self.room.pk]),
            {'email': 'test@hotel.com'}
        )
        self.assertTrue(
            Subscription.objects.filter(user=self.user, room=self.room).exists()
        )

    def test_subscribe_requires_login(self):
        url = reverse('subscribe_room', args=[self.room.pk])
        response = self.client.post(
            url,
            {'email': 'test@hotel.com'}
        )
        login_url = reverse('login')
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertFalse(
            Subscription.objects.filter(user=self.user, room=self.room).exists()
        )

    def test_subscribe_duplicate_does_not_create_extra(self):
        self.client.login(username='testuser', password='TestPass123!')
        url = reverse('subscribe_room', args=[self.room.pk])
        self.client.post(url, {'email': 'test@hotel.com'})
        self.client.post(url, {'email': 'test@hotel.com'})
        self.assertEqual(
            Subscription.objects.filter(user=self.user, room=self.room).count(), 1
        )

    # -- Unsubscribe --

    def test_unsubscribe_removes_subscription(self):
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        self.client.login(username='testuser', password='TestPass123!')
        self.client.post(reverse('unsubscribe_room', args=[self.room.pk]))
        self.assertFalse(
            Subscription.objects.filter(user=self.user, room=self.room).exists()
        )

    def test_unsubscribe_requires_login(self):
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        self.client.post(reverse('unsubscribe_room', args=[self.room.pk]))
        # Still exists because not logged in
        self.assertTrue(
            Subscription.objects.filter(user=self.user, room=self.room).exists()
        )

    # -- Observer notification --

    def test_observer_notified_when_availability_changes(self):
        """Observer is notified (NotificationLog created) when room availability changes."""
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        original = self.room.is_available
        # Toggle availability to trigger the observer signal
        self.room.is_available = not original
        self.room.save()
        self.assertEqual(
            NotificationLog.objects.filter(subscription__user=self.user).count(), 1
        )

    def test_observer_not_notified_when_no_change(self):
        """Observer is NOT notified if availability did not change."""
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        # Save without changing availability
        self.room.save()
        self.assertEqual(
            NotificationLog.objects.filter(subscription__user=self.user).count(), 0
        )

    def test_notification_log_message_content(self):
        """Notification log message mentions the room title and status."""
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        self.room.is_available = not self.room.is_available
        self.room.save()
        log = NotificationLog.objects.filter(subscription__user=self.user).first()
        self.assertIn(self.room.title, log.message)

    def test_multiple_subscribers_all_notified(self):
        """All subscribers of a room are notified when availability changes."""
        user2 = User.objects.create_user(username='user2', password='pass2', email='u2@hotel.com')
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        Subscription.objects.create(user=user2, room=self.room, email='u2@hotel.com')
        self.room.is_available = not self.room.is_available
        self.room.save()
        self.assertEqual(
            NotificationLog.objects.filter(subscription__room=self.room).count(), 2
        )

    # -- Subscriptions page --

    def test_my_subscriptions_page_status(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('my_subscriptions'))
        self.assertEqual(response.status_code, 200)

    def test_my_subscriptions_shows_user_subscriptions(self):
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('my_subscriptions'))
        self.assertIn(self.room, [s.room for s in response.context['subscriptions']])

    def test_room_detail_shows_subscription_status(self):
        Subscription.objects.create(user=self.user, room=self.room, email='test@hotel.com')
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertTrue(response.context['is_subscribed'])

    def test_room_detail_not_subscribed_by_default(self):
        self.client.login(username='testuser', password='TestPass123!')
        response = self.client.get(reverse('room_detail', args=[self.room.pk]))
        self.assertFalse(response.context['is_subscribed'])


# ── Auth Views Tests ─────────────────────────────────────────────────────────

class AuthViewsTest(TestCase):
    """Тести сторінок реєстрації, входу та виходу."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='existinguser', password='TestPass123!', email='exist@hotel.com'
        )

    # -- Register --

    def test_register_page_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/register.html')

    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'StrongPass99!',
            'password2': 'StrongPass99!',
        })
        self.assertRedirects(response, '/')
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # User is logged in after registration
        response2 = self.client.get(reverse('my_subscriptions'))
        self.assertEqual(response2.status_code, 200)

    def test_register_invalid_password_mismatch(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'StrongPass99!',
            'password2': 'WrongPass99!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_register_redirects_if_already_authenticated(self):
        self.client.login(username='existinguser', password='TestPass123!')
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, '/')

    # -- Login --

    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, '/')

    def test_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'existinguser',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/login.html')

    def test_login_redirects_if_already_authenticated(self):
        self.client.login(username='existinguser', password='TestPass123!')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, '/')

    def test_login_respects_next_param(self):
        response = self.client.post(
            reverse('login') + '?next=/rooms/',
            {'username': 'existinguser', 'password': 'TestPass123!', 'next': '/rooms/'}
        )
        self.assertRedirects(response, '/rooms/')

    # -- Logout --

    def test_logout_post(self):
        self.client.login(username='existinguser', password='TestPass123!')
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, '/')
        # After logout, my_subscriptions should redirect to login
        response2 = self.client.get(reverse('my_subscriptions'))
        self.assertRedirects(response2, '/login/?next=/subscriptions/')
