from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.db import database_sync_to_async
from django.contrib.contenttypes.models import ContentType

import json

from friend.models import FriendRequest, FriendList
from notification.models import Notification
from notification.utils import LazyNotificationEncoder
from notification.constants import *
from chat.exceptions import ClientError


class NotificationConsumer(AsyncJsonWebsocketConsumer):
	"""
	Passing data to and from header.html. Notifications are displayed as "drop-downs" in the nav bar.
	There is two major categories of notifications:
		1. General Notifications
			1. FriendRequest
			2. FriendList
		1. Chat Notifications
			1. UnreadChatRoomMessages
	"""

	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		print("NotificationConsumer: connect: " + str(self.scope["user"]) )
		await self.accept()


	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		print("NotificationConsumer: disconnect")


	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		command = content.get("command", None)
		print("NotificationConsumer: receive_json. Command: " + command)
		try:
			if command == "get_general_notifications":
				payload = await get_general_notifications(self.scope["user"], content.get("page_number", None))
				if payload == None:
					pass
				else:
					payload = json.loads(payload)
					await self.send_general_notifications_payload(payload['notifications'], payload['new_page_number'])
			elif command == "accept_friend_request":
				try:
					notification_id = content['notification_id']
					payload = await accept_friend_request(self.scope['user'], notification_id)
					if payload == None:
						raise NotificationClientError("Something went wrong. Try refreshing the browser.")
					else:
						payload = json.loads(payload)
						await self.send_updated_friend_request_notification(payload['notification'])
				except Exception as e:
					print("EXCEPTION: NotificationConsumer: " + str(e))
					pass
		except Exception as e:
			print("EXCEPTION: receive_json: " + str(e))
			pass

	async def display_progress_bar(self, shouldDisplay):
		print("NotificationConsumer: display_progress_bar: " + str(shouldDisplay)) 
		await self.send_json(
			{
				"progress_bar": shouldDisplay,
			},
		)

	async def send_general_notifications_payload(self, notifications, new_page_number):
		"""
		Called by receive_json when ready to send a json array of the notifications
		"""
		#print("NotificationConsumer: send_general_notifications_payload")
		await self.send_json(
			{
				"general_msg_type": GENERAL_MSG_TYPE_NOTIFICATIONS_PAYLOAD,
				"notifications": notifications,
				"new_page_number": new_page_number,
			},
		)

	async def send_updated_friend_request_notification(self, notification):
		"""
		After a friend request is accepted or declined, send the updated notification to template
		payload contains 'notification' and 'response':
		1. payload['notification']
		2. payload['response']
		"""
		await self.send_json(
			{
				"general_msg_type": GENERAL_MSG_TYPE_UPDATED_NOTIFICATION,
				"notification": notification,
			},
		)



@database_sync_to_async
def get_general_notifications(user, page_number):
	"""
	Get General Notifications with Pagination (next page of results).
	This is for appending to the bottom of the notifications list.
	General Notifications are:
	1. FriendRequest
	2. FriendList
	"""
	if user.is_authenticated:
		friend_request_ct = ContentType.objects.get_for_model(FriendRequest)
		friend_list_ct = ContentType.objects.get_for_model(FriendList)
		notifications = Notification.objects.filter(target=user, content_type__in=[friend_request_ct, friend_list_ct]).order_by('-timestamp')
		p = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)

		payload = {}
		if len(notifications) > 0:
			if int(page_number) <= p.num_pages:
				s = LazyNotificationEncoder()
				serialized_notifications = s.serialize(p.page(page_number).object_list)
				payload['notifications'] = serialized_notifications
				new_page_number = int(page_number) + 1
				payload['new_page_number'] = new_page_number
		else:
			return None
	else:
		raise ClientError("User must be authenticated to get notifications.")

	return json.dumps(payload)


@database_sync_to_async
def accept_friend_request(user, notification_id):
    """
    Accept a friend request
    """
    payload = {}
    if user.is_authenticated:
        try:
            notification = Notification.objects.get(pk=notification_id)
            friend_request = notification.content_object
            # confirm this is the correct user
            if friend_request.receiver == user:
                # accept the request and get the updated notification
                updated_notification = friend_request.accept()

                # return the notification associated with this FriendRequest
                s = LazyNotificationEncoder()
                payload['notification'] = s.serialize([updated_notification])[0]
                return json.dumps(payload)
        except Notification.DoesNotExist:
            raise NotificationClientError("An error occurred with that notification. Try refreshing the browser.")
    return None







