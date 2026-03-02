from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.room_list, name='room_list'),
    path('rooms/<int:pk>/', views.room_detail, name='room_detail'),
    path('rooms/<int:pk>/subscribe/', views.subscribe_room, name='subscribe_room'),
    path('rooms/<int:pk>/unsubscribe/', views.unsubscribe_room, name='unsubscribe_room'),
    path('subscriptions/', views.my_subscriptions, name='my_subscriptions'),
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]

