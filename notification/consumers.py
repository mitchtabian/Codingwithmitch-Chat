from django.contrib.auth import get_user_model
from django.conf import settings
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.paginator import Paginator
from django.core.serializers import serialize
from channels.db import database_sync_to_async

from datetime import datetime
import json
from time import sleep
from enum import Enum

from notification.utils import LazyNotificationEncoder
from notification.models import Notification
from notification.exceptions import NotificationClientError
from notification.constants import *

User = get_user_model()

DEFAULT_NOTIFICATION_PAGE_SIZE = 5


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
            if command == "get_notifications":
                await self.display_progress_bar(True)
                payload = await self.get_notifications(content.get("page_number", None))
                if payload == None:
                    await self.pagination_exhausted()
                else:
                    payload = json.loads(payload)
                    await self.send_notifications_payload(payload['notifications'], payload['new_page_number'])
                await self.display_progress_bar(False)
            elif command == "refresh_notifications":
                payload = await self.refresh_notifications(content['oldest_timestamp'])
                if payload == None:
                    raise NotificationClientError("Something went wrong. Try refreshing the browser.")
                else:
                    payload = json.loads(payload)
                    await self.send_refreshed_notifications_payload(payload['notifications'])
        except Exception as e:
            await self.display_progress_bar(False)
            # Catch any errors and send it back
            errorData = {}
            try:
                if e.code:
                    errorData['error'] = e.code
                if e.message:
                    errorData['message'] = e.message
            except:
                errorData['message'] = "An unknown error occurred"
            await self.send_json(errorData)


    async def pagination_exhausted(self):
        print("Pagination DONE... No more notifications.")
        await self.send_json(
            {
                "msg_type": MSG_TYPE_PAGINATION_EXHAUSTED,
            },
        )

    async def send_notifications_payload(self, notifications, new_page_number):
        """
        Called by receive_json when ready to send a json array of the notifications
        """
        print("NotificationConsumer: send_notifications_payload")
        await self.send_json(
            {
                "msg_type": MSG_TYPE_NOTIFICATIONS_PAYLOAD,
                "notifications": notifications,
                "new_page_number": new_page_number,
            },
        )

    async def send_refreshed_notifications_payload(self, notifications):
        """
        Called by receive_json when ready to send a json array of the notifications
        """
        print("NotificationConsumer: send_refreshed_notifications_payload")
        await self.send_json(
            {
                "msg_type": MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD,
                "notifications": notifications,
            },
        )


    async def display_progress_bar(self, shouldDisplay):
        print("NotificationConsumer: display_progress_bar: " + str(shouldDisplay)) 
        await self.send_json(
            {
                "progress_bar": shouldDisplay,
            },
        )

    @database_sync_to_async
    def get_notifications(self, page_number):
        """
        Get Notifications with Pagination (next page of results).
        This is for appending to the bottom of the notifications list.
        """
        user = self.scope["user"]
        if user.is_authenticated:
            notifications = Notification.objects.filter(target=user).order_by('-timestamp')
            p = Paginator(notifications, DEFAULT_NOTIFICATION_PAGE_SIZE)

            # sleep 1s for testing
            # sleep(1)  
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
            raise NotificationClientError("User must be authenticated to get notifications.")

        return json.dumps(payload)



    @database_sync_to_async
    def refresh_notifications(self, oldest_timestamp):
        """
        Retrieve the notifications newer than the older one on the screen.
        This will accomplish 2 things:
        1. Notifications currently visible will be updated
        2. Any new notifications will be appending to the top of the list
        """
        payload = {}
        user = self.scope["user"]
        if user.is_authenticated:
            timestamp = oldest_timestamp[0:oldest_timestamp.find("+")] # remove timezone because who cares
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
            notifications = Notification.objects.filter(target=user, timestamp__gte=timestamp).order_by('-timestamp')

            s = LazyNotificationEncoder()
            payload['notifications'] = s.serialize(notifications)
        else:
            raise NotificationClientError("User must be authenticated to get notifications.")

        return json.dumps(payload)        












