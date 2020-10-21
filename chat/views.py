from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponse
from django.conf import settings
from itertools import chain

import json

from account.models import Account
from chat.models import PrivateChatRoom, RoomChatMessage
from chat.utils import find_or_create_private_chat

DEBUG = False

def private_chat_room_view(request, *args, **kwargs):
	user = request.user

	# Redirect them if not authenticated
	if not user.is_authenticated:
		return redirect("login")

	context = {}

	# 1. Find all the rooms this user is a part of 
	rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
	rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

	# 2. merge the lists
	rooms = list(chain(rooms1, rooms2))

	"""
	m_and_f:
		[{"message": "hey", "friend": "Mitch"}, {"message": "You there?", "friend": "Blake"},]
	Where message = The most recent message
	"""
	m_and_f = [] 
	for room in rooms:
		# Figure out which user is the "other user" (aka friend)
		if room.user1 == user:
			friend = room.user2
		else:
			friend = room.user1
		m_and_f.append({
			'message': "", # blank msg for now (since we have no messages)
			'friend': friend
		})
	context['m_and_f'] = m_and_f

	context['debug'] = DEBUG
	context['debug_mode'] = settings.DEBUG
	return render(request, "chat/room.html", context)



# Ajax call to return a private chatroom or create one if does not exist
def create_or_return_private_chat(request, *args, **kwargs):
	user1 = request.user
	payload = {}
	if user1.is_authenticated:
		if request.method == "POST":
			user2_id = request.POST.get("user2_id")
			try:
				user2 = Account.objects.get(pk=user2_id)
				chat = find_or_create_private_chat(user1, user2)
				payload['response'] = "Successfully got the chat."
				payload['chatroom_id'] = chat.id
			except Account.DoesNotExist:
				payload['response'] = "Unable to start a chat with that user."
	else:
		payload['response'] = "You can't start a chat if you are not authenticated."
	return HttpResponse(json.dumps(payload), content_type="application/json")








