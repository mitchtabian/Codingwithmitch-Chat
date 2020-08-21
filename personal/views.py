from django.shortcuts import render, redirect
from django.conf import settings

from chat.models import Room
from chat.utils import create_new_room

def home_screen_view(request):
	context = {}

	rooms = Room.objects.all()
	print("rooms: " + str(rooms))
	context['rooms'] = rooms

	user = request.user
	if user.is_authenticated and user.is_staff:
		if request.method == "POST":
			title = request.POST.get("new_room_title")
			private = False
			if request.POST.get("authorization_private"):
				private = True
			room = create_new_room(title, private, user)
			return redirect("home")

	return render(request, "personal/home.html", context)