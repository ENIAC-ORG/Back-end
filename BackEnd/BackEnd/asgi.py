"""
ASGI config for BackEnd project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

 
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from channels.auth import AuthMiddlewareStack
import django
from django.urls import path
import os
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup() 


from chat.consumers import ChatConsumer 


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/<int:room_id>/", ChatConsumer.as_asgi()),
        ])
    ),
})
