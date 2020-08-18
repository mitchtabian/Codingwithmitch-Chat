from django.shortcuts import render
from django.conf import settings
from django.core.serializers import serialize
from django.core.paginator import Paginator
import json
from django.http import HttpResponse

from chat.models import Room, RoomChatMessage
from chat.utils import LazyRoomChatMessageEncoder

DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE = 20
DEBUG = False

def room_view(request, *args, **kwargs):
	context = {}
	context["BASE_URL"] = settings.BASE_URL
	room_id = kwargs.get("room_id")
	context["room_id"] = room_id
	context["room_title"] = Room.objects.get(pk=room_id)
	context['debug'] = DEBUG
	return render(request, "chat/room.html", context)

from time import sleep

def get_room_chat_messages(request, *args, **kwargs):

	if request.GET:
		has_joined_room = request.GET.get("has_joined_room")
		print("has joined room: " + str(has_joined_room))
		if has_joined_room == "True":
			room_id = request.GET.get("room_id")
			room = Room.objects.get(pk=room_id)
			qs = RoomChatMessage.objects.by_room(room)
			page_number = request.GET.get("page_number")
			p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

			sleep(1)
			payload = {}
			messages_data = None
			new_page_number = int(page_number)	
			print("num pages: " + str(p.num_pages))
			if new_page_number <= p.num_pages:
				new_page_number = new_page_number + 1
				s = LazyRoomChatMessageEncoder()
				payload['messages'] = s.serialize(p.page(page_number).object_list)
			else:
				payload['messages'] = "None"
			payload['page_number'] = new_page_number
			return HttpResponse(json.dumps(payload), content_type="application/json")
	return HttpResponse("Something went wrong.")


