from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
import os
import cv2
import json
import base64

from account.models import Account
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm

TEMP_PROFILE_IMAGE_NAME = "_temp_profile_image.png"


# save image to /temp/
# load image with cv2
# crop image with cv2
# save image to /temp/
# return cropped imageUrl in payload
def crop_image(request, *args, **kwargs):
	payload = {}
	if request.POST:
		try:
			imageString = request.POST.get("image")
			username = kwargs.get("username")
			url = save_temp_profile_image_from_base64String(imageString, username)
			img = cv2.imread(url)

			cropX = int(float(str(request.POST.get("cropX"))))
			cropY = int(float(str(request.POST.get("cropY"))))
			cropWidth = int(float(str(request.POST.get("cropWidth"))))
			cropHeight = int(float(str(request.POST.get("cropHeight"))))
			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]
			cv2.imwrite(url, crop_img)
			payload['success'] = True
			payload['cropped_image_url'] = url
		except Exception as e:
			payload['success'] = False
			payload['exception'] = e
	return HttpResponse(json.dumps(payload), content_type="application/json")


def save_temp_profile_image_from_base64String(imageString, username):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		url = os.path.join(settings.TEMP , username + TEMP_PROFILE_IMAGE_NAME)
		storage = FileSystemStorage(location=url)
		image = base64.b64decode(imageString)
		with storage.open('', 'wb+') as destination:
			destination.write(image)
			destination.close()
		return url
	except Exception as e:
		print("exception: " + str(e))
		if str(e) == INCORRECT_PADDING_EXCEPTION:
			imageString += "=" * ((4 - len(imageString) % 4) % 4)
			return save_temp_profile_image_from_base64String(imageString, username)
	return None


def account_view(request, *args, **kwargs):
	context = {}
	username = kwargs.get("username")
	account = Account.objects.filter(username=username).first()
	if account:
		context['username'] = account.username
		context['email'] = account.email
		context['profile_image'] = account.profile_image
	else:
		return HttpResponse("Something went wrong.")
	return render(request, "account/account.html", context)


def edit_account_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("/login/")
	username = kwargs.get("username")
	account = Account.objects.filter(username=username).first()
	if account.pk != request.user.pk:
		return HttpResponse("You cannot edit someone elses profile.")
	context = {}
	if request.POST:
			form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
			if form.is_valid():
				form.save()
				new_username = form.cleaned_data['username']
				return redirect("account:account", username=new_username)
			else:
				form = AccountUpdateForm(request.POST, instance=request.user,
					initial={
						"email": account.email, 
						"username": account.username,
					}
				)
				context['form'] = form
	else:
		form = AccountUpdateForm(
			initial={
					"email": account.email, 
					"username": account.username,
				}
			)
		context['form'] = form
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	return render(request, "account/edit_account.html", context)


def login_view(request):
	return render(request, "account/login.html", {})


def register_view(request):
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			login(request, account)
			return redirect('home')
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', context)


def logout_view(request):
	logout(request)
	return redirect('/')


def login_view(request):
	context = {}

	user = request.user
	if user.is_authenticated: 
		return redirect("home")

	if request.POST:
		form = AccountAuthenticationForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				return redirect("home")

	else:
		form = AccountAuthenticationForm()

	context['login_form'] = form

	# print(form)
	return render(request, "account/login.html", context)









