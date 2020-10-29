from channels.generic.websocket import AsyncJsonWebsocketConsumer



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


	async def display_progress_bar(self, shouldDisplay):
		print("NotificationConsumer: display_progress_bar: " + str(shouldDisplay)) 
		await self.send_json(
			{
				"progress_bar": shouldDisplay,
			},
		)

	









