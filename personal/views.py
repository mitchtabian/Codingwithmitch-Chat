from django.shortcuts import render
from django.conf import settings

def home_screen_view(request):
	context = {}
	context["BASE_URL"] = settings.BASE_URL
	context["chat_name"] = settings.DEFAULT_CHAT_NAME


	return render(request, "personal/home.html", context)