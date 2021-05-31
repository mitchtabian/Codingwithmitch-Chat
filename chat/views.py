from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.utils import timezone
from urllib.parse import urlencode
import json
from itertools import chain
from datetime import datetime
import pytz


from friend.models import FriendList
from account.models import Account
from chat.models import PrivateChatRoom, RoomChatMessage
from chat.utils import find_or_create_private_chat


DEBUG = False


def private_chat_room_view(request, *args, **kwargs):
	room_id = request.GET.get("room_id")
	user = request.user
	if not user.is_authenticated:
		base_url = reverse('login')
		query_string = urlencode({'next': f"/chat/?room_id={room_id}"})
		url = f"{base_url}?{query_string}"
		return redirect(url)

	context = {}

	context['m_and_f'] = get_recent_chatroom_messages(user)

	context["BASE_URL"] = settings.BASE_URL
	if room_id:
		context["room_id"] = room_id
	context['debug'] = DEBUG
	context['debug_mode'] = settings.DEBUG
	return render(request, "chat/room.html", context)


def get_recent_chatroom_messages(user):
	"""
	sort in terms of most recent chats (users that you most recently had conversations with)
	"""
	# 1. Find all the rooms this user is a part of 
	rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
	rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

	# 2. merge the lists
	rooms = list(chain(rooms1, rooms2))

	# 3. find the newest msg in each room
	m_and_f = []
	for room in rooms:
		# Figure out which user is the "other user" (aka friend)
		if room.user1 == user:
			friend = room.user2
		else:
			friend = room.user1

		# confirm you are even friends (in case chat is left active somehow)
		friend_list = FriendList.objects.get(user=user)
		if not friend_list.is_mutual_friend(friend):
			chat = find_or_create_private_chat(user, friend)
			chat.is_active = False
			chat.save()
		else:	
			# find newest msg from that friend in the chat room
			try:
				message = RoomChatMessage.objects.filter(room=room, user=friend).latest("timestamp")
			except RoomChatMessage.DoesNotExist:
				# create a dummy message with dummy timestamp
				today = datetime(
					year=1950, 
					month=1, 
					day=1, 
					hour=1,
					minute=1,
					second=1,
					tzinfo=pytz.UTC
				)
				message = RoomChatMessage(
					user=friend,
					room=room,
					timestamp=today,
					content="",
				)
			m_and_f.append({
				'message': message,
				'friend': friend
			})

	return sorted(m_and_f, key=lambda x: x['message'].timestamp, reverse=True)


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
				print("Successfully got the chat")
				payload['response'] = "Successfully got the chat."
				payload['chatroom_id'] = chat.id
			except Account.DoesNotExist:
				payload['response'] = "Unable to start a chat with that user."
	else:
		payload['response'] = "You can't start a chat if you are not authenticated."
	return HttpResponse(json.dumps(payload), content_type="application/json")








