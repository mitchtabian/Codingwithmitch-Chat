from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.conf import settings
from itertools import chain

from chat.models import PrivateChatRoom, RoomChatMessage

DEBUG = False

def private_chat_room_room_view(request, *args, **kwargs):
	room_id = request.GET.get("room_id")
	user = request.user

	# Redirect them if not authenticated
	if not user.is_authenticated:
		base_url = reverse('login')
		query_string = urlencode({'next': f"/chat/?room_id={room_id}"})
		url = f"{base_url}?{query_string}"
		return redirect(url)

	context = {}
	if room_id:
		context["room_id"] = room_id

	# 1. Find all the rooms this user is a part of 
	rooms1 = PrivateChatRoom.objects.filter(user1=user, is_active=True)
	rooms2 = PrivateChatRoom.objects.filter(user2=user, is_active=True)

	# 2. merge the lists
	rooms = list(chain(rooms1, rooms2))
	print(str(len(rooms)))

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


