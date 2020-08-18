from django.contrib.auth import get_user_model
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
import json

from chat.models import RoomChatMessage
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
            # elif command == "increment_page":
            #     # increment page number
            #     await self.increment_page(content['page'], content['room_id'])
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
        
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            # Notify the group that someone joined
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_id,
                    "profile_image": self.scope["user"].profile_image.url,
                    "username": self.scope["user"].username,
                }
            )

        # Store that we're in the room
        self.rooms.add(room_id)
        # Add them to the group so they get room messages
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )
        # # Get previous chat room messages
        # messages = await self.get_room_chat_messages(room)
        # print(messages)

        # Instruct their client to finish opening the room
        await self.send_json({
            "join": str(room.id),
            "title": room.title,
            # "messages": messages,
        })


    async def leave_room(self, room_id):
        """
        Called by receive_json when someone sent a leave command.
        """
        # The logged-in user is in our scope thanks to the authentication ASGI middleware
        print("ChatConsumer: leave_room")
        room = await get_room_or_error(room_id, self.scope["user"])

        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            # Notify the group that someone left
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "room_id": room_id,
                    "profile_image": self.scope["user"].profile_image.url,
                    "username": self.scope["user"].username,
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
        await self.create_room_chat_message(room, self.scope["user"], message)
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "profile_image": self.scope["user"].profile_image.url,
                "username": self.scope["user"].username,
                "message": message,
            }
        )


    # These helper methods are named by the types we send - so chat.join becomes chat_join
    async def chat_join(self, event):
        """
        Called when someone has joined our chat.
        """
        # Send a message down to the client
        print("ChatConsumer: chat_join: " + str(event["username"]))
        if event["username"]:
            await self.send_json(
                {
                    "msg_type": settings.MSG_TYPE_ENTER,
                    "room": event["room_id"],
                    "profile_image": event["profile_image"],
                    "username": event["username"],
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
                },
            )


    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        print("ChatConsumer: chat_message")
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_MESSAGE,
                "room": event["room_id"],
                "username": event["username"],
                "profile_image": event["profile_image"],
                "message": event["message"],
            },
        )


    # async def increment_page(self, page, room_id):
    #     try:
    #         room = await get_room_or_error(room_id, self.scope["user"])
    #     except ClientError as e:
    #         errorData = {}
    #         errorData['error'] = e.code
    #         if e.message:
    #             errorData['message'] = e.message
    #         await self.send_json(errorData)
    #         return

    #     new_page = int(page) + 1
    #     print("incrementing page: " + str(page))
    #     messages = await self.get_room_chat_messages(room, int(page)*DEFAULT_PAGE_SIZE)
    #     print(messages)

    #     await self.send_json({
    #         "msg_type": settings.MSG_TYPE_INCREMENT_PAGE,
    #         "new_page": str(new_page),
    #         "messages": messages
    #     })


    # @database_sync_to_async
    # def get_room_chat_messages(self, room):
    #     messages =[]
    #     for message in RoomChatMessage.objects.by_room(room):
    #         messages.append({
    #             "username": message.user.username,
    #             "profile_image": message.user.profile_image.url,
    #             "message": message.content,
    #         })
    #     return json.dumps(messages)

    @database_sync_to_async
    def create_room_chat_message(self, room, user, message):
        return RoomChatMessage.objects.create(user=user, room=room, content=message)
















