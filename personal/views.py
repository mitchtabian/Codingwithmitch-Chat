from django.shortcuts import render, redirect
from django.conf import settings


def home_screen_view(request):
	context = {}

	return render(request, "personal/home.html", context)













