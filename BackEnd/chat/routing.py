from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:id_room>/', consumers.ChatConsumer.as_asgi()),
]
