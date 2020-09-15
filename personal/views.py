from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import json
from datetime import datetime    

from notification.models import Notification
from friend.models import FriendRequest
from public_chat.models import PublicChatRoom

DEBUG = False

def home_screen_view(request):
	context = {}
	user = request.user
	if user.is_authenticated:
		context['debug'] = DEBUG

	# Retrieve the "General" chat room
	obj, created = PublicChatRoom.objects.get_or_create(title="General")
	context['public_chat'] = obj

	return render(request, "personal/home.html", context)











