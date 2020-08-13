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
import requests
import tempfile
from django.core import files

from account.models import Account, get_profile_image_filepath
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"



# save image to /temp/
# load image with cv2
# crop image with cv2
# save image to /temp/

def crop_image(request, *args, **kwargs):
	payload = {}
	user = request.user
	if request.POST and user.is_authenticated:
		try:
			imageString = request.POST.get("image")
			url = save_temp_profile_image_from_base64String(imageString, user)
			img = cv2.imread(url)

			cropX = int(float(str(request.POST.get("cropX"))))
			cropY = int(float(str(request.POST.get("cropY"))))
			cropWidth = int(float(str(request.POST.get("cropWidth"))))
			cropHeight = int(float(str(request.POST.get("cropHeight"))))
			if cropX < 0:
				cropX = 0
			if cropY < 0: # There is a bug with cropperjs. y can be negative.
				cropY = 0
			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]

			cv2.imwrite(url, crop_img)
			filename = os.path.basename(url)
			mediaUrl = settings.BASE_URL + "/media/temp/" + str(user.pk) + "/" + filename

			request = requests.get(mediaUrl, stream=True)

			# Was the request OK?
			if request.status_code != requests.codes.ok:
				raise Exception("Something went wrong. Try another image.")

			# Create a temporary file
			lf = tempfile.NamedTemporaryFile()
			# Read the streamed image in sections
			for block in request.iter_content(1024 * 8):
				# If no more file then stop
				if not block:
					break

				# Write image block to temporary file
				lf.write(block)

			# Save the temporary image to the model#
			# This saves the model so be sure that is it valid
			user.profile_image.save("profile_image.png", files.File(lf))

			payload['result'] = "success"
			payload['cropped_profile_image'] = mediaUrl
			
		except Exception as e:
			print("exception: " + str(e))
			payload['result'] = "error"
			payload['exception'] = str(e)
	return HttpResponse(json.dumps(payload), content_type="application/json")


def save_temp_profile_image_from_base64String(imageString, user):
	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
	try:
		if not os.path.exists(settings.TEMP):
			os.mkdir(settings.TEMP)
		if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
			os.mkdir(settings.TEMP + "/" + str(user.pk))
		url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
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
			return save_temp_profile_image_from_base64String(imageString, user)
	return None


def account_view(request, *args, **kwargs):
	context = {}
	username = kwargs.get("username")
	account = Account.objects.filter(username=username).first()
	if account:
		context['username'] = account.username
		context['email'] = account.email
		context['profile_image'] = account.profile_image
		context['hide_email'] = account.hide_email
	else:
		return HttpResponse("Something went wrong.")
	return render(request, "account/account.html", context)


def edit_account_view(request, *args, **kwargs):
	if not request.user.is_authenticated:
		return redirect("login")
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
				return redirect("account:view", username=new_username)
			else:
				form = AccountUpdateForm(request.POST, instance=request.user,
					initial={
						"email": account.email, 
						"username": account.username,
						"profile_image": account.profile_image,
					}
				)
				context['form'] = form
	else:
		form = AccountUpdateForm(
			initial={
					"email": account.email, 
					"username": account.username,
					"profile_image": account.profile_image,
				}
			)
		context['form'] = form
	context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
	return render(request, "account/edit_account.html", context)


def register_view(request):
	user = request.user
	if user.is_authenticated: 
		return HttpResponse("You are already authenticate as " + str(user.email))

	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email').lower()
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			login(request, account)
			destination = kwargs.get("next")
			if destination:
				return redirect(destination)
			return redirect('home')
		else:
			context['registration_form'] = form

	else:
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', context)


def logout_view(request):
	print("LOGGING OUT")
	logout(request)
	return redirect("home")


def login_view(request, *args, **kwargs):
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
	return render(request, "account/login.html", context)









