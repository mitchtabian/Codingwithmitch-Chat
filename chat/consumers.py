from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
import json

User = get_user_model()

# Order of operations:
# send from html template using socket.send(JSON.stringify({....
# Receive msg in websocket_receive
# websocket_receive sends message to channel "group" using custom type ("cwm_chat_message")
# cwm_chat_message sends message to template
# template receives message in onmessage
class ChatConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        print("websocket_connect: " + str(event))
        chat_name = str(self.scope['url_route']['kwargs']['chat_name'])
        print("websocket_connect: chat_name: " + chat_name)
        self.room_name = chat_name
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.send({
            "type": "websocket.accept"
        })


    async def websocket_receive(self, event):
        print("websocket_receive: " + str(event))
        user = self.scope['user']
        username = user.username
        message_data = {}
        message_data["message"] = json.loads(event['text'])['message']
        message_data["user"] = username
        final_message_data = json.dumps(message_data)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "cmw_chat_message",
                "message": final_message_data
            }
        )

    async def cmw_chat_message(self, event):
        print("cmw_chat_message: " + str(event))
        await self.send({
            "type": "websocket.send",
            "text": event['message']
        })


    async def websocket_disconnect(self, event):
        print("websocket_disconnect: " + str(event))
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )















