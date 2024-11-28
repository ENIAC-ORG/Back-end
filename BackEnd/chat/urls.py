from django.urls import path
from .views import CreateRoom
from . import views

urlpatterns = [
    # path('', views.room_list, name='room_list'),  
    # path('<str:room_name>/', views.room, name='room'),  
    path('create/', CreateRoom.as_view(), name='create_room'),  
    #path('create/', views.create_room, name='create_room'), 
]
