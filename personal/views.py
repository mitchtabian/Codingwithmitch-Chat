from django.shortcuts import render
from django.conf import settings

def home_screen_view(request):
	context = {}
	context['debug_mode'] = settings.DEBUG
	context['room_id'] = "1"
	return render(request, "personal/home.html", context)








