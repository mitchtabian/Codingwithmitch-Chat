from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.http import HttpResponse
from django.conf import settings

from account.models import Account
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm


def account_view(request, *args, **kwargs):
	context = {}
	username = kwargs.get("username")
	print("USERNAME: " + str(username))
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









