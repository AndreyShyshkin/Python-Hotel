from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def room_list(request):
    return render(request, 'rooms.html')

def room_detail(request):
    return render(request, 'room_detail.html')