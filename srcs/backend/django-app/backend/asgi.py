"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.urls import path
from django.core.asgi import get_asgi_application

asgi_application=get_asgi_application()

from tpong.game.networking.PongClientConsumer import PongClientConsumer
from api.consumer import UserConsumer
from .middleware import ChannelsJWTAuthMiddleware

application = ProtocolTypeRouter({
	"http": asgi_application,
	"websocket": ChannelsJWTAuthMiddleware(URLRouter([
		path('ws/tpong/', PongClientConsumer.as_asgi()),
		path('ws/user/', UserConsumer.as_asgi())
	]))
}) 

