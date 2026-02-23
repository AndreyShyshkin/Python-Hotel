from django.shortcuts import render, get_object_or_404
from .models import Room, RoomCategory, Amenity


def home(request):
    return render(request, 'index.html')


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
    return render(request, 'room_detail.html', {
        'room': room,
        'similar_rooms': similar_rooms,
    })

