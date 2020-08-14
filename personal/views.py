from django.shortcuts import render, redirect
from django.conf import settings

from chat.models import Room

def home_screen_view(request):
	context = {}

	rooms = Room.objects.all()
	context['rooms'] = rooms

	if request.method == "POST":
		title = request.POST.get("new_room_title")
		staff_only = False
		if request.POST.get("authorization_staff_only"):
			staff_only = True
		print(str(staff_only))
		# room = Room(title=title, staff_only=staff_only)
		return redirect("home")

	return render(request, "personal/home.html", context)