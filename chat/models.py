from django.conf import settings

from django.db import models



class Room(models.Model):
    """
    A room for people to chat in.
    """

    # Room title
    title = models.CharField(max_length=255, unique=True, blank=False,)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def group_name(self):
        """
        Returns the Channels Group name that sockets should subscribe to to get sent
        messages as they are generated.
        """
        return "room-%s" % self.id


class RoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = RoomChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs

class RoomChatMessage(models.Model):
    """
    Chat message created by a user inside a Room
    """
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room                = models.ForeignKey(Room, on_delete=models.CASCADE)
    timestamp           = models.DateTimeField(auto_now_add=True)
    content             = models.CharField(max_length=255, unique=True, blank=False,)

    objects = RoomChatMessageManager()

    def __str__(self):
        return self.content














