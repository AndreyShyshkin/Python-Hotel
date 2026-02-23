from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'index.html')

def room_list(request):
    rooms = Room.objects.select_related('category').all() 
    search = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    
    if search:
        rooms = rooms.filter(title__icontains=search) 

    if category_id:
        rooms = rooms.filter(category_id=category_id)
        
    context = {'rooms': rooms}
    return render(request, 'rooms.html', context)

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk) 
    return render(request, 'room_detail.html', {'room': room})