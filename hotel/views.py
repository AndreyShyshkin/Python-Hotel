from django.shortcuts import render, get_object_or_404

def home(request):
    return render(request, 'index.html')

def room_list(request):
    rooms = Room.objects.all()
    search = request.GET.get('search', '').strip()
    
    if search:
        rooms = rooms.filter(title__contains=search) 
        
    context = {'rooms': rooms}
    return render(request, 'rooms.html', context)

def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk) 
    return render(request, 'room_detail.html', {'room': room})