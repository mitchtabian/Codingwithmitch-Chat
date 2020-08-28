from django.contrib.auth import get_user_model
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

import json

User = get_user_model()


class NotificationConsumer(AsyncJsonWebsocketConsumer):

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
            if command == "on_open":
                print("A new connection is opened.")
            elif command == "leave":
                # Leave the room
                await self.leave_room(content["room"])
            elif command == "send":
                await self.send_room(content["room"], content["message"])
        except ClientError as e:
            # Catch any errors and send it back
            errorData = {}
            errorData['error'] = e.code
            if e.message:
                errorData['message'] = e.message
            await self.send_json(errorData)





















