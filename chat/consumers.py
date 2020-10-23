from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers import serialize

import json

from chat.models import RoomChatMessage, PrivateChatRoom
from friend.models import FriendList
from account.utils import LazyAccountEncoder

class ChatConsumer(AsyncJsonWebsocketConsumer):


	async def connect(self):
		"""
		Called when the websocket is handshaking as part of initial connection.
		"""
		print("ChatConsumer: connect: " + str(self.scope["user"]))

		# let everyone connect. But limit read/write to authenticated users
		await self.accept()

		# the room_id will define what it means to be "connected". If it is not None, then the user is connected.
		self.room_id = None


	async def receive_json(self, content):
		"""
		Called when we get a text frame. Channels will JSON-decode the payload
		for us and pass it as the first argument.
		"""
		# Messages will have a "command" key we can switch on
		print("ChatConsumer: receive_json")
		command = content.get("command", None)
		try:
			if command == "join":
				print("joining room: " + str(content['room']))
				await self.join_room(content["room"])
			elif command == "leave":
				pass
			elif command == "send":
				pass
			elif command == "get_room_chat_messages":
				pass
			elif command == "get_user_info":
				room = await get_room_or_error(content['room_id'], self.scope["user"])
				payload = get_user_info(room, self.scope["user"])
				if payload != None:
					payload = json.loads(payload)
					await self.send_user_info_payload(payload['user_info'])
				else:
					raise Exception("Something went wrong retrieving the other users account details.")
		except Exception as e:
			pass


	async def disconnect(self, code):
		"""
		Called when the WebSocket closes for any reason.
		"""
		# Leave the room
		print("ChatConsumer: disconnect")


	async def join_room(self, room_id):
		"""
		Called by receive_json when someone sent a join command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
		print("ChatConsumer: join_room: " + str(room_id))
		try:
			room = await get_room_or_error(room_id, self.scope["user"])
		except Exception as e:
			return
		# Instruct their client to finish opening the room
		await self.send_json({
			"join": str(room.id),
		})

	async def leave_room(self, room_id):
		"""
		Called by receive_json when someone sent a leave command.
		"""
		# The logged-in user is in our scope thanks to the authentication ASGI middleware
		print("ChatConsumer: leave_room")


	async def send_room(self, room_id, message):
		"""
		Called by receive_json when someone sends a message to a room.
		"""
		print("ChatConsumer: send_room")

	# These helper methods are named by the types we send - so chat.join becomes chat_join
	async def chat_join(self, event):
		"""
		Called when someone has joined our chat.
		"""
		# Send a message down to the client
		print("ChatConsumer: chat_join: " + str(self.scope["user"].id))

	async def chat_leave(self, event):
		"""
		Called when someone has left our chat.
		"""
		# Send a message down to the client
		print("ChatConsumer: chat_leave")

	async def chat_message(self, event):
		"""
		Called when someone has messaged our chat.
		"""
		# Send a message down to the client
		print("ChatConsumer: chat_message")

	async def send_messages_payload(self, messages, new_page_number):
		"""
		Send a payload of messages to the ui
		"""
		print("ChatConsumer: send_messages_payload. ")

	async def send_user_info_payload(self, user_info):
		"""
		Send a payload of user information to the ui
		"""
		print("ChatConsumer: send_user_info_payload. ")
		await self.send_json(
			{
				"user_info": user_info,
			},
		)

	async def display_progress_bar(self, is_displayed):
		"""
		1. is_displayed = True
		- Display the progress bar on UI
		2. is_displayed = False
		- Hide the progress bar on UI
		"""
		print("DISPLAY PROGRESS BAR: " + str(is_displayed))


@database_sync_to_async
def get_room_or_error(room_id, user):
	"""
	Tries to fetch a room for the user, checking permissions along the way.
	"""
	try:
		room = PrivateChatRoom.objects.get(pk=room_id)
	except PrivateChatRoom.DoesNotExist:
		raise Exception("Invalid room.")

	# Is this user allowed in the room? (must be user1 or user2)
	if user != room.user1 and user != room.user2:
		raise Exception("You do not have permission to join this room.")

	# Are the users in this room friends?
	friend_list = FriendList.objects.get(user=user).friends.all()
	if not room.user1 in friend_list:
		if not room.user2 in friend_list:
			raise Exception("You must be friends to chat.")
	return room


# I don't think this requires @database_sync_to_async since we are just accessing a model field
# https://docs.djangoproject.com/en/3.1/ref/models/instances/#refreshing-objects-from-database
def get_user_info(room, user):
	"""
	Retrieve the user info for the user you are chatting with
	"""
	try:
		# Determine who is who
		other_user = room.user1
		if other_user == user:
			other_user = room.user2

		payload = {}
		s = LazyAccountEncoder()
		# convert to list for serializer and select first entry (there will be only 1)
		payload['user_info'] = s.serialize([other_user])[0] 
		return json.dumps(payload)
	except Exception as e:
		print("EXCEPTION: " + str(e))
	print("none I guess?...")
	return None   

















