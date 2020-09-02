from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

from chat.consumers import ChatConsumer
from notification.consumers import NotificationConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(
		AuthMiddlewareStack(
			URLRouter([
					path('chat/<room_id>/', ChatConsumer),
					path('', NotificationConsumer)
				])
		)
	),
})














