from django.urls import path

from chat.views import(
	room_view,
	get_room_chat_messages,
	get_room_connected_users,
)

urlpatterns = [
    path('<room_id>/', room_view, name='room'),
    path('<room_id>/get_room_chat_messages/', get_room_chat_messages, name='get-room-chat-messages'),
    path('<room_id>/get_room_connected_users/', get_room_connected_users, name='get-room-connected-users'),
]

app_name = 'chat'