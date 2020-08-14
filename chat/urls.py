from django.urls import path

from chat.views import(
	room_view,
)

urlpatterns = [
    path('<room_id>/', room_view, name='room'),
]

app_name = 'chat'