from channels.db import database_sync_to_async
from django.core.serializers.python import Serializer
from django.conf import settings

from .exceptions import ClientError
from .models import PrivateChatRoom, RoomChatMessage
from friend.models import FriendList


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



class LazyRoomChatMessageEncoder(Serializer):
    def get_dump_object(self, obj):
        dump_object = {}
        dump_object.update({'user_id': str(obj.user.id)})
        dump_object.update({'username': str(obj.user.username)})
        dump_object.update({'message': str(obj.content)})
        dump_object.update({'profile_image': str(obj.user.profile_image.url)})
        return dump_object










