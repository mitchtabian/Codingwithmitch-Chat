from django.contrib.auth import get_user_model
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.utils import timezone

import json
from time import sleep

from account.models import Account
from chat.models import RoomChatMessage, PrivateChatRoom, UnreadChatRoomMessages
from chat.exceptions import ClientError
from chat.constants import *
from chat.utils import LazyRoomChatMessageEncoder, calculate_timestamp
from friend.models import FriendList

User = get_user_model()

DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE = 20


"""
Json payload identifiers:
1. type
2. messages_payload
3. join
4. leave
5. send
6. msg_type
    - See chat.constants for all possible types

"""


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
                print("SEND: " + str(content["message"]))
                await self.send_room(content["room"], content["message"])
            elif command == "get_room_chat_messages":
                await self.display_progress_bar(True)
                room = await get_room_or_error(content['room_id'], self.scope["user"])
                payload = await get_room_chat_messages(room, content['page_number'])
                if payload != None:
                    payload = json.loads(payload)
                    await self.send_messages_payload(payload['messages'], payload['new_page_number'])
                else:
                    raise ClientError(204,"Something went wrong retrieving the chatroom messages.")
                await self.display_progress_bar(False)
            
        except ClientError as e:
            await self.display_progress_bar(False)
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
        await connect_user(room, self.scope["user"])

        await on_user_connected(room, self.scope["user"])

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
        await disconnect_user(room, self.scope["user"])

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
        await append_unread_msg_if_not_connected(room, room.user1, connected_users, message)
        await append_unread_msg_if_not_connected(room, room.user2, connected_users, message)

        await create_room_chat_message(room, self.scope["user"], message)
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
                    "msg_type": MSG_TYPE_ENTER,
                    "room": event["room_id"],
                    "profile_image": event["profile_image"],
                    "username": event["username"],
                    "user_id": event["user_id"],
                    "message": event["username"] + " connected.",
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
                    "msg_type": MSG_TYPE_LEAVE,
                    "room": event["room_id"],
                    "profile_image": event["profile_image"],
                    "username": event["username"],
                    "user_id": event["user_id"],
                    "message": event["username"] + " disconnected.",
                },
            )


    async def chat_message(self, event):
        """
        Called when someone has messaged our chat.
        """
        # Send a message down to the client
        print("ChatConsumer: chat_message from user #" + str(event["user_id"]))

        timestamp = calculate_timestamp(timezone.now())

        await self.send_json(
            {
                "msg_type": MSG_TYPE_MESSAGE,
                "room": event["room_id"],
                "username": event["username"],
                "user_id": event["user_id"],
                "profile_image": event["profile_image"],
                "message": event["message"],
                "natural_timestamp": timestamp,
            },
        )




    async def send_messages_payload(self, messages, new_page_number):
        """
        Send a payload of messages to the ui
        """
        print("ChatConsumer: send_messages_payload.")

        await self.send_json(
            {
                "messages_payload": "messages_payload",
                "messages": messages,
                "new_page_number": new_page_number,
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
        await self.send_json(
            {
                "display_progress_bar": is_displayed
            }
        )

@database_sync_to_async
def create_room_chat_message(room, user, message):
    return RoomChatMessage.objects.create(user=user, room=room, content=message)


@database_sync_to_async
def connect_user(room, user):
    # add user to connected_users list
    account = Account.objects.get(pk=user.id)
    return room.connect_user(account)


@database_sync_to_async
def disconnect_user(room, user):
    # remove from connected_users list
    account = Account.objects.get(pk=user.id)
    return room.disconnect_user(account)


# If the user is not connected to the chat, increment "unread messages" count
@database_sync_to_async
def append_unread_msg_if_not_connected(room, user, connected_users, message):
    if not user in connected_users: 
        unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
        unread_msgs.most_recent_message = message
        unread_msgs.count += 1
        unread_msgs.save()
    return

# When a user connects, reset their unread message count
@database_sync_to_async
def on_user_connected(room, user):
    # confirm they are in the connected users list
    connected_users = room.connected_users.all()
    if user in connected_users:
        # reset count
        unread_msgs = UnreadChatRoomMessages.objects.get(room=room, user=user)
        unread_msgs.count = 0
        unread_msgs.save()
    return


# This decorator turns this function from a synchronous function into an async one
# we can call from our async consumers, that handles Django DBs correctly.
# For more, see http://channels.readthedocs.io/en/latest/topics/databases.html
@database_sync_to_async
def get_room_or_error(room_id, user):
    """
    Tries to fetch a room for the user, checking permissions along the way.
    """
    # Check if the user is logged in
    # if not user.is_authenticated:
    #     raise ClientError("USER_HAS_TO_LOGIN", "You must login.")
    # Find the room they requested (by ID)
    try:
        room = PrivateChatRoom.objects.get(pk=room_id)
    except PrivateChatRoom.DoesNotExist:
        raise ClientError("ROOM_INVALID", "Invalid room.")
    # Check permissions

    # Is this user allowed in the room? (must be user1 or user2)
    if user != room.user1 and user != room.user2:
        raise ClientError("ROOM_ACCESS_DENIED", "You do not have permission to join this room.")

    # Are the users in this room friends?
    friend_list = FriendList.objects.get(user=user).friends.all()
    if not room.user1 in friend_list:
        if not room.user2 in friend_list:
            raise ClientError("ROOM_ACCESS_DENIED", "You must be friends to chat.")
    return room


@database_sync_to_async
def get_room_chat_messages(room, page_number):
    try:
        qs = RoomChatMessage.objects.by_room(room)
        p = Paginator(qs, DEFAULT_ROOM_CHAT_MESSAGE_PAGE_SIZE)

        sleep(1) # for testing
        payload = {}
        messages_data = None
        new_page_number = int(page_number)  
        if new_page_number <= p.num_pages:
            new_page_number = new_page_number + 1
            s = LazyRoomChatMessageEncoder()
            payload['messages'] = s.serialize(p.page(page_number).object_list)
        else:
            payload['messages'] = "None"
        payload['new_page_number'] = new_page_number
        return json.dumps(payload)
    except Exception as e:
        print("EXCEPTION: " + str(e))
        return None
       




















