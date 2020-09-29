from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path, re_path

from public_chat.consumers import PublicChatConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					path('public_chat/<room_id>/', PublicChatConsumer),
			])
		)
	),
})