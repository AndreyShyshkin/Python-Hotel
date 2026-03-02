from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Room, RoomCategory, Amenity, Subscription, NotificationLog


# ── Auth Views ──────────────────────────────────────────────────────────────

def register_view(request):
    """Custom registration page."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Ласкаво просимо, {user.username}! Реєстрація пройшла успішно.')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """Custom login page."""
    if request.user.is_authenticated:
        return redirect('home')
    next_url = request.GET.get('next', '/')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'З поверненням, {user.username}!')
            return redirect(request.POST.get('next', next_url) or '/')
        else:
            messages.error(request, 'Невірний логін або пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'auth/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    """Logout via POST."""
    logout(request)
    messages.info(request, 'Ви вийшли з системи.')
    return redirect('home')


# ── Hotel Views ──────────────────────────────────────────────────────────────

def home(request):
    featured_rooms = (
        Room.objects.select_related('category')
        .prefetch_related('amenities')
        .filter(is_available=True)
        .order_by('price')[:5]
    )
    total_rooms      = Room.objects.count()
    available_rooms  = Room.objects.filter(is_available=True).count()
    total_categories = RoomCategory.objects.count()
    context = {
        'featured_rooms':   featured_rooms,
        'total_rooms':       total_rooms,
        'available_rooms':   available_rooms,
        'total_categories':  total_categories,
    }
    return render(request, 'index.html', context)


def room_list(request):
    
    rooms = Room.objects.select_related('category').prefetch_related('amenities').all()

    # --- фільтри ---
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    capacity = request.GET.get('capacity', '')
    available = request.GET.get('available', '')
    amenity_ids = request.GET.getlist('amenities')
    sort = request.GET.get('sort', '')

    if search:
        rooms = rooms.filter(title__icontains=search)

    if category_id:
        rooms = rooms.filter(category_id=category_id)

    if price_min:
        rooms = rooms.filter(price__gte=price_min)

    if price_max:
        rooms = rooms.filter(price__lte=price_max)

    if capacity:
        cap = int(capacity)
        if cap >= 4:
            rooms = rooms.filter(capacity__gte=4)
        else:
            rooms = rooms.filter(capacity=cap)

    if available == 'on':
        rooms = rooms.filter(is_available=True)

    if amenity_ids:
        for aid in amenity_ids:
            rooms = rooms.filter(amenities__id=aid)
        rooms = rooms.distinct()

    sort_map = {
        'price-asc':  'price',
        'price-desc': '-price',
        'name-asc':   'title',
        'name-desc':  '-title',
    }
    rooms = rooms.order_by(sort_map.get(sort, 'id'))

    capacity_choices = [
        (0, 'Будь-яка'),
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4+'),
    ]

    def qs_without(*keys):
        params = request.GET.copy()
        for k in keys:
            params.pop(k, None)
        return params.urlencode()

    context = {
        'rooms': rooms,
        'categories': RoomCategory.objects.all(),
        'amenities': Amenity.objects.all(),
        'capacity_choices': capacity_choices,
        'filters': {
            'search': search,
            'category_id': category_id,
            'price_min': price_min or 0,
            'price_max': price_max or 15000,
            'capacity': capacity,
            'available': available,
            'amenity_ids': amenity_ids,
            'sort': sort,
        },
        'qs_no_search': qs_without('search'),
        'qs_no_category': qs_without('category'),
        'qs_no_available': qs_without('available'),
        'total': rooms.count(),
    }
    return render(request, 'rooms.html', context)


def room_detail(request, pk):
    room = get_object_or_404(
        Room.objects.select_related('category').prefetch_related('amenities'),
        pk=pk
    )
    similar_rooms = (
        Room.objects.select_related('category')
        .filter(category=room.category)
        .exclude(pk=pk)[:3]
    )

    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = Subscription.objects.filter(user=request.user, room=room).exists()

    return render(request, 'room_detail.html', {
        'room': room,
        'similar_rooms': similar_rooms,
        'is_subscribed': is_subscribed,
    })


@login_required
@require_POST
def subscribe_room(request, pk):
    """Observer: subscribe the current user to room availability changes."""
    room = get_object_or_404(Room, pk=pk)
    email = request.POST.get('email', '').strip()
    if not email:
        email = request.user.email

    _, created = Subscription.objects.get_or_create(
        user=request.user,
        room=room,
        defaults={'email': email},
    )
    if created:
        messages.success(request, f'Ви підписалися на сповіщення про номер «{room.title}».')
    else:
        # Update email if provided
        if email:
            Subscription.objects.filter(user=request.user, room=room).update(email=email)
        messages.info(request, 'Ви вже підписані на цей номер.')
    return redirect('room_detail', pk=pk)


@login_required
@require_POST
def unsubscribe_room(request, pk):
    """Observer: unsubscribe the current user from room availability changes."""
    room = get_object_or_404(Room, pk=pk)
    deleted, _ = Subscription.objects.filter(user=request.user, room=room).delete()
    if deleted:
        messages.success(request, f'Ви відписалися від сповіщень про номер «{room.title}».')
    else:
        messages.info(request, 'Ви не були підписані на цей номер.')
    return redirect('room_detail', pk=pk)


@login_required
def my_subscriptions(request):
    """Show all subscriptions and notification logs for the current user."""
    subscriptions = (
        Subscription.objects
        .filter(user=request.user)
        .select_related('room', 'room__category')
        .prefetch_related('notifications')
        .order_by('-created_at')
    )
    return render(request, 'subscriptions.html', {'subscriptions': subscriptions})


