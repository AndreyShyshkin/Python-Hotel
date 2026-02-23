from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def room_list(request):
    rooms = Room.objects.all()
    context = {'rooms': rooms}
    return render(request, 'rooms.html', context)

def room_detail(request, pk):
    room = Room.objects.get(pk=pk) 
    return render(request, 'room_detail.html', {'room': room})