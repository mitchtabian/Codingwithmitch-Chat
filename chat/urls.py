from django.urls import path

from chat.views import(
	private_chat_room_room_view,
	get_room_chat_messages,
	create_or_return_private_chat,
)

urlpatterns = [
    path('create_or_return_private_chat/', create_or_return_private_chat, name='create-or-return-private-chat'),
    path('<room_id>/', private_chat_room_room_view, name='private-chat-room'),
    path('<room_id>/get_room_chat_messages/', get_room_chat_messages, name='get-room-chat-messages'),
]

app_name = 'chat'