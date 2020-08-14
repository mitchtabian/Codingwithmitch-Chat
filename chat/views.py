from django.shortcuts import render
from django.conf import settings

from chat.models import Room


def room_view(request, *args, **kwargs):
	context = {}
	context["BASE_URL"] = settings.BASE_URL

	room_id = kwargs.get("room_id")
	context["room_id"] = room_id
	context["room_title"] = Room.objects.get(pk=room_id)


	return render(request, "chat/room.html", context)




