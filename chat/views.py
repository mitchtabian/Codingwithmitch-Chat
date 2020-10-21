from django.shortcuts import render, redirect
from django.conf import settings

from chat.models import PrivateChatRoom, RoomChatMessage

DEBUG = False

def private_chat_room_view(request, *args, **kwargs):
	user = request.user

	# Redirect them if not authenticated
	if not user.is_authenticated:
		return redirect("login")

	context = {}
	context['debug'] = DEBUG
	context['debug_mode'] = settings.DEBUG
	return render(request, "chat/room.html", context)


