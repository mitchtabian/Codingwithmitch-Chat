from django.shortcuts import render
from django.http import HttpResponse
import json

from friend.models import FriendRequest, FriendList
from account.models import Account


def send_friend_request(request, *args, **kwargs):
	user = request.user
	payload = {}
	if request.method == "GET" and user.is_authenticated:
		user_id = kwargs.get("user_id")
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
	if request.method == "GET" and user.is_authenticated:
		user_id = kwargs.get("user_id")
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
	if request.method == "GET" and user.is_authenticated:
		user_id = kwargs.get("user_id")
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
		


















