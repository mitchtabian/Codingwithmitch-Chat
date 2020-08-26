from django.contrib.auth import get_user_model
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async

import json

from account.models import Account
from chat.models import RoomChatMessage, PrivateChatRoom, UnreadChatRoomMessages
from chat.exceptions import ClientError
from chat.utils import get_room_or_error

User = get_user_model()


# Example taken from:
# https://github.com/andrewgodwin/channels-examples/blob/master/multichat/chat/consumers.py
class ChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        print("ChatConsumer: connect: " + str(self.scope["user"]))

        # if not self.scope["user"].is_authenticated:
        #     await self.close()
        # else:
        #     # Accept the connection
        #     await self.accept()
        #     # Store which rooms the user has joined on this connection
        #     self.rooms = set()

        # let everyone connect. But limit read/write to authenticated users
        await self.accept()
        self.rooms = set()


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
                # Make them join the room
                await self.join_room(content["room"])
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


    async def disconnect(self, code):
        """
        Called when the WebSocket closes for any reason.
        """
        # Leave all the rooms we are still in
        print("ChatConsumer: disconnect")
        try:
            for room_id in list(self.rooms):
                await self.leave_room(room_id)
        except Exception:
            pass


    async def join_room(self, room_id):
        """
        Called by receive_json when someone sent a join command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware (AuthMiddlewareStack)
        
        print("ChatConsumer: join_room")
        try:
            room = await get_room_or_error(room_id, self.scope["user"])
        except ClientError as e:
            errorData = {}
            errorData['error'] = e.code
            if e.message:
                errorData['message'] = e.message
            await self.send_json(errorData)
            return

        # Add user to "connected_users" list
        await self.connect_user(room, self.scope["user"])

        await self.on_user_connected(room, self.scope["user"])

        # Store that we're in the room
        self.rooms.add(room_id)
        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )

        # Instruct their client to finish opening the room
        print("JOIN: " + str(self.scope["user"].id)) 
        await self.send_json({
            "join": str(room.id),
            "profile_image": self.scope["user"].profile_image.url,
            "username": self.scope["user"].username,
            "user_id": self.scope["user"].id,
        })

        if self.scope["user"].is_authenticated:
            # if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
                # Notify the group that someone joined
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_id,
                    "profile_image": self.scope["user"].profile_image.url,
                    "username": self.scope["user"].username,
                    "user_id": self.scope["user"].id,
                }
            )


    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        print("ChatConsumer: leave_room")
        room = await get_room_or_error(room_id, self.scope["user"])

        # Remove user from "connected_users" list
        await self.disconnect_user(room, self.scope["user"])

        #if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
        # Notify the group that someone left
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.leave",
                "room_id": room_id,
                "profile_image": self.scope["user"].profile_image.url,
                "username": self.scope["user"].username,
                "user_id": self.scope["user"].id,
            }
        )

        # Remove that we're in the room
        self.rooms.discard(room_id)
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.id),
        })



    async def send_room(self, room_id, message):
        """
        Called by receive_json when someone sends a message to a room.
        """
        # Check they are in this room
        print("ChatConsumer: send_room")
        if room_id not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED", "Room access denied")
        # Get the room and send to the group about it
        room = await get_room_or_error(room_id, self.scope["user"])

        # get list of connected_users
        connected_users = room.connected_users.all()
        await self.append_unread_msg_if_not_connected(room, room.user1, connected_users, message)
        await self.append_unread_msg_if_not_connected(room, room.user2, connected_users, message)

        await self.create_room_chat_message(room, self.scope["user"], message)
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "profile_image": self.scope["user"].profile_image.url,
                "username": self.scope["user"].username,
                "user_id": self.scope["user"].id,
                "message": message,
            }
        )


    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        print("ChatConsumer: chat_join: " + str(self.scope["user"].id))
        if event["username"]:
            await self.send_json(
                {
                    "msg_type": settings.MSG_TYPE_ENTER,
                    "room": event["room_id"],
                    "profile_image": event["profile_image"],
                    "username": event["username"],
                    "user_id": event["user_id"],
                },
            )


    async def chat_leave(self, event):
        """
        Called when someone has left our chat.
        """
        # Send a message down to the client
        print("ChatConsumer: chat_leave: " + str(event["username"]))
        if event["username"]:
            await self.send_json(
                {
                    "msg_type": settings.MSG_TYPE_LEAVE,
                    "room": event["room_id"],
                    "profile_image": event["profile_image"],
                    "username": event["username"],
                    "user_id": event["user_id"],
                },
            )


    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        print("ChatConsumer: chat_message from user #" + str(event["user_id"]))

        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_MESSAGE,
                "room": event["room_id"],
                "username": event["username"],
                "user_id": event["user_id"],
                "profile_image": event["profile_image"],
                "message": event["message"],
            },
        )

    @database_sync_to_async
    def create_room_chat_message(self, room, user, message):
        return RoomChatMessage.objects.create(user=user, room=room, content=message)


    @database_sync_to_async
    def connect_user(self, room, user):
        # add user to connected_users list
        account = Account.objects.get(pk=user.id)
        return room.connect_user(account)


    @database_sync_to_async
    def disconnect_user(self, room, user):
        # remove from connected_users list
        account = Account.objects.get(pk=user.id)
        return room.disconnect_user(account)


    # If the user is not connected to the chat, increment "unread messages" count
    @database_sync_to_async
    def append_unread_msg_if_not_connected(self, room, user, connected_users, message):
        if not user in connected_users: 
            unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
            unread_msgs.most_recent_message = message
            unread_msgs.count += 1
            unread_msgs.save()
        return

    # When a user connects, reset their unread message count
    @database_sync_to_async
    def on_user_connected(self, room, user):
        # confirm they are in the connected users list
        connected_users = room.connected_users.all()
        if user in connected_users:
            # reset count
            unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
            unread_msgs.count = 0
            unread_msgs.save()
        return







