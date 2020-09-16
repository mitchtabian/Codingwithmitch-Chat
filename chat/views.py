from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from urllib.parse import urlencode
import json

from friend.models import FriendList
from account.models import Account
from chat.models import PrivateChatRoom, RoomChatMessage



DEBUG = False


def private_chat_room_room_view(request, *args, **kwargs):
	room_id = request.GET.get("room_id")
	user = request.user
	if not user.is_authenticated:
		base_url = reverse('login')
		query_string =  urlencode({'next': f"/chat/?room_id={room_id}"})
		url = f"{base_url}?{query_string}"
		return redirect(url)

	context = {}

	try:
		friend_list = FriendList.objects.get(user=user)
		context['friends'] = friend_list.friends.all()
	except FriendList.DoesNotExist:
		pass

	context["BASE_URL"] = settings.BASE_URL
	if room_id:
		context["room_id"] = room_id
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











