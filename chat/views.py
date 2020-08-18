from django.shortcuts import render
from django.conf import settings
from django.core.serializers import serialize
from django.core.paginator import Paginator
from django.http import HttpResponse
import json
from time import sleep

from account.models import Account
from chat.models import Room, RoomChatMessage
from chat.utils import LazyRoomChatMessageEncoder

DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE = 20
DEBUG = False

def room_view(request, *args, **kwargs):
	context = {}
	context["BASE_URL"] = settings.BASE_URL
	room_id = kwargs.get("room_id")
	context["room_id"] = room_id
	room = Room.objects.get(pk=room_id)
	context["room_title"] = room.title
	context['debug'] = DEBUG
	context['connected_users'] = room.connected_users.all()
	print("connected users: " + str(context['connected_users']))

	return render(request, "chat/room.html", context)


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

			# sleep(1) # for testing
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






import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    print("Random string of length", length, "is:", result_str)
    return result_str

def insert_room_chat_messages(num_messages):
	mitch = Account.objects.get(pk=1)
	jessica = Account.objects.get(pk=5)
	room = Room.objects.get(pk=room_id)
	for x in range(0, num_messages):
		content = str(x) + " " + get_random_string(25)
		if x % 2 == 0:
			usr = mitch
		else:
			usr = jessica
		message = RoomChatMessage(user=usr, room=room, content=content)
		message.save()











