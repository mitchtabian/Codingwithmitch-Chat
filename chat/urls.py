from django.urls import path

from chat.views import(
	room_view,
	get_room_chat_messages,
)

urlpatterns = [
    path('<room_id>/', room_view, name='room'),
    path('<room_id>/get_room_chat_messages/', get_room_chat_messages, name='get-room-chat-messages'),
]

app_name = 'chat'