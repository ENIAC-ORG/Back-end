"""
ASGI config for BackEnd project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
#from chat.routing import websocket_urlpatterns  # Import the WebSocket URL patterns
from django.urls import path
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BackEnd.settings')
django.setup() 


from chat.consumers import ChatConsumer 
# # Initialize the Django ASGI application
# django_asgi_app = get_asgi_application()

# # Define the ASGI application
# application = ProtocolTypeRouter({
#     "http": django_asgi_app,  # Handles HTTP requests
#     "websocket": AuthMiddlewareStack(
#         URLRouter(
#             [path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi())]
#         )
#     ),
# })

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            [path("ws/chat/<str:room_name>/", ChatConsumer.as_asgi())]
        ])
    ),
})
