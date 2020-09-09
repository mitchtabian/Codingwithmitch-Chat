from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
import json
from datetime import datetime    

from notification.models import Notification
from friend.models import FriendRequest

DEBUG = False

def home_screen_view(request):
	context = {}
	user = request.user
	if user.is_authenticated:
		context['debug'] = DEBUG

	return render(request, "personal/home.html", context)













