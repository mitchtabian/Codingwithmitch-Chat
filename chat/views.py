from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.core.serializers import serialize
from django.core.paginator import Paginator
from django.http import HttpResponse
from urllib.parse import urlencode
import json
from time import sleep

from account.models import Account
from account.utils import LazyAccountEncoder
from chat.models import PrivateChatRoom, RoomChatMessage
from chat.utils import LazyRoomChatMessageEncoder


DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE = 20
DEBUG = False


def private_chat_room_room_view(request, *args, **kwargs):
	room_id = kwargs.get("room_id")
	user = request.user
	if not user.is_authenticated:
		base_url = reverse('login')
		query_string =  urlencode({'next': f"/chat/{room_id}/"})
		url = f"{base_url}?{query_string}"
		return redirect(url)
	context = {}
	context["BASE_URL"] = settings.BASE_URL
	context["room_id"] = room_id
	room = PrivateChatRoom.objects.get(pk=room_id)
	context['user1'] = room.user1
	context['user2'] = room.user2
	context['debug'] = DEBUG
	return render(request, "chat/room.html", context)


# Ajax call to return a private chatroom or create one if does not exist
def create_or_return_private_chat(request, *args, **kwargs):
	print("create_or_return_private_chat")
	user1 = request.user
	payload = {}
	if user1.is_authenticated:
		if request.method == "POST":
			user2_id = request.POST.get("user2_id")
			try:
				user2 = Account.objects.get(pk=user2_id)
				chat = find_or_create_private_chat(user1, user2)
				print("Successfully got the chat")
				payload['response'] = "Successfully got the chat."
				payload['chatroom_id'] = chat.id
			except Account.DoesNotExist:
				payload['response'] = "Unable to start a chat with that user."
	else:
		payload['response'] = "You can't start a chat if you are not authenticated."
	return HttpResponse(json.dumps(payload), content_type="application/json")


def find_or_create_private_chat(user1, user2):
	try:
		chat = PrivateChatRoom.objects.get(user1=user1, user2=user2)
	except PrivateChatRoom.DoesNotExist:
		try:
			chat = PrivateChatRoom.objects.get(user1=user2, user2=user1)
		except PrivateChatRoom.DoesNotExist:
			chat = PrivateChatRoom(user1=user1, user2=user2)
			chat.save()
	return chat


def get_room_chat_messages(request, *args, **kwargs):

	if request.GET:
		has_joined_room = request.GET.get("has_joined_room")
		# print("has joined room: " + str(has_joined_room))
		if has_joined_room == "True":
			room_id = request.GET.get("room_id")
			room = PrivateChatRoom.objects.get(pk=room_id)
			qs = RoomChatMessage.objects.by_room(room)
			page_number = request.GET.get("page_number")
			p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

			# sleep(1) # for testing
			payload = {}
			messages_data = None
			new_page_number = int(page_number)	
			# print("num pages: " + str(p.num_pages))
			if new_page_number <= p.num_pages:
				new_page_number = new_page_number + 1
				s = LazyRoomChatMessageEncoder()
				payload['messages'] = s.serialize(p.page(page_number).object_list)
			else:
				payload['messages'] = "None"
			payload['page_number'] = new_page_number
			return HttpResponse(json.dumps(payload), content_type="application/json")
	return HttpResponse("Something went wrong.")




# Testing
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    # print("Random string of length", length, "is:", result_str)
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











