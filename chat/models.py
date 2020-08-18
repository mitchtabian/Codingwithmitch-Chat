from django.conf import settings
from django.db import models




class Room(models.Model):
    """
    A room for people to chat in.
    """

    # Room title
    title               = models.CharField(max_length=255, unique=True, blank=False,)

    # If only "staff" users are allowed (is_staff on django's User)
    staff_only          = models.BooleanField(default=False)

    connected_users     = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True) 

    def __str__(self):
        return self.title

    def add_user(self, user):
        """
        return true if user is added to the connected_users list
        """
        is_user_added = False
        if user.is_authenticated:
            if not user in self.connected_users.all():
                self.connected_users.add(user)
                is_user_added = True
        return is_user_added

    def remove_user(self, user):
        """
        return true if user is removed from the connected_users list
        """
        is_user_removed = False
        if user.is_authenticated:
            if user in self.connected_users.all():
                self.connected_users.remove(user)
                is_user_removed = True
        return is_user_removed

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














