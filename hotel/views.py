from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'index.html')

def room_list(request):
    
    rooms = Room.objects.select_related('category').prefetch_related('amenities').all()

   
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    capacity = request.GET.get('capacity', '')
    available = request.GET.get('available', '')
    amenity_ids = request.GET.getlist('amenities') 

    
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
        

    context = {'rooms': rooms}
    return render(request, 'rooms.html', context)

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk) 
    return render(request, 'room_detail.html', {'room': room})