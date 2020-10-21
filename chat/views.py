from django.shortcuts import render, redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.conf import settings

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
	context['debug'] = DEBUG
	context['debug_mode'] = settings.DEBUG
	return render(request, "chat/room.html", context)


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