from django.shortcuts import render, redirect
from django.http import HttpResponse
import json

from friend.models import FriendRequest, FriendList
from account.models import Account


def friend_requests(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		user_id = kwargs.get("user_id")
		account = Account.objects.get(pk=user_id)
		if account == user:
			friend_requests = FriendRequest.objects.filter(receiver=account)
			context['friend_requests'] = friend_requests
		else:
			return HttpResponse("You can't view another users friend requets.")
	else:
		redirect("login")
	return render(request, "friend/friend_requests.html", context)


def friends_list_view(request, *args, **kwargs):
	context = {}
	user = request.user
	if user.is_authenticated:
		username = kwargs.get("username")
		if username:
			try:
				this_user = Account.objects.get(username=username)
				context['this_user'] = this_user
			except Account.DoesNotExist:
				return HttpResponse("That user does not exist.")
			try:
				friend_list = FriendList.objects.get(user=this_user)
			except FriendList.DoesNotExist:
				return HttpResponse(f"Could not find a friends list for {this_user.username}")
			
			# Must be friends to view a friends list
			if user != this_user:
				if not user in friend_list.friends.all():
					return HttpResponse("You must be friends to view their friends list.")
			friends = [] # [(friend1, True), (friend2, False), ...]
			# get the authenticated users friend list
			auth_user_friend_list = FriendList.objects.get(user=user)
			for friend in friend_list.friends.all():
				friends.append((friend, auth_user_friend_list.is_mutual_friend(friend)))
			context['friends'] = friends
	else:		
		return HttpResponse("You must be friends to view their friends list.")
	return render(request, "friend/friend_list.html", context)


def send_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receiver_user_id")
		if user_id:
			receiver = Account.objects.get(pk=user_id)
			obj, created = FriendRequest.objects.get_or_create(sender=user, receiver=receiver)
			if not created: 
				# There is already a request pending.
				payload['response'] = "You already sent them a friend request."
			elif created:
				payload['response'] = "Friend request sent."
			else:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to sent a friend request."
	else:
		payload['response'] = "You must be authenticated to send a friend request."
	return HttpResponse(json.dumps(payload), content_type="application/json")
			


def cancel_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receiver_user_id")
		if user_id:
			receiver = Account.objects.get(pk=user_id)
			friend_request = FriendRequest.objects.get(sender=user, receiver=receiver)
			if friend_request: 
				# found the request. Now decline it
				friend_request.delete()
				payload['response'] = "Friend request canceled."
			else:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to cancel that friend request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to cancel a friend request."
	return HttpResponse(json.dumps(payload), content_type="application/json")
			

def remove_friend(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		user_id = request.POST.get("receiver_user_id")
		if user_id:
			try:
				removee = Account.objects.get(pk=user_id)
				friend_list = FriendList.objects.get(user=user)
				friend_list.unfriend(removee)
				payload['response'] = "Successfully removed that friend."
			except Exception as e:
				payload['response'] = f"Something went wrong: {str(e)}"
		else:
			payload['response'] = "There was an error. Unable to remove that friend."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to remove a friend."
	return HttpResponse(json.dumps(payload), content_type="application/json")
		



def accept_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		sender_user_id = request.POST.get("sender_user_id")
		if sender_user_id:
			sender = Account.objects.get(pk=sender_user_id)
			friend_request = FriendRequest.objects.get(sender=sender, receiver=user)
			if friend_request: 
				# found the request. Now accept it
				friend_request.accept()
				friend_request.delete()
				payload['response'] = "Friend request accepted."
			else:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to accept that friend request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to accept a friend request."
	return HttpResponse(json.dumps(payload), content_type="application/json")
		



def decline_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "POST" and user.is_authenticated:
		sender_user_id = request.POST.get("sender_user_id")
		if sender_user_id:
			sender = Account.objects.get(pk=sender_user_id)
			friend_request = FriendRequest.objects.get(sender=sender, receiver=user)
			if friend_request: 
				# found the request. Now decline it
				friend_request.delete()
				payload['response'] = "Friend request declined."
			else:
				payload['response'] = "Something went wrong."
		else:
			payload['response'] = "Unable to decline that friend request."
	else:
		# should never happen
		payload['response'] = "You must be authenticated to decline a friend request."
	return HttpResponse(json.dumps(payload), content_type="application/json")
		





















