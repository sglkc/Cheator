"""
ASGI config for login project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from accounts.consumers import VideoConsumer  # Ganti 'yourapp' dengan nama aplikasi Django kamu

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'login.settings') 

# Aplikasi ASGI
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # Menggunakan ASGI untuk HTTP
    "websocket": AuthMiddlewareStack(  # Tambahkan dukungan untuk WebSockets
        URLRouter([
            path('ws/video_feed/', VideoConsumer.as_asgi()),  # Tambahkan routing WebSocket untuk video feed
        ])
    ),
})


