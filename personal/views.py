from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from notification.models import Notification
from friend.models import FriendRequest


def home_screen_view(request):
	context = {}
	user = request.user
	if user.is_authenticated:
		notifications = Notification.objects.filter(target=user).order_by('-timestamp')
		context['notifications'] = notifications

	return render(request, "personal/home.html", context)













