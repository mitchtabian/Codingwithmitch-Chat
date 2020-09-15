from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class PublicChatRoom(models.Model):

	# Room title
	title 				= models.CharField(max_length=255, unique=True, blank=False,)

	# All users who are currently connected to the chat and authenticated
	# They are identified by a unique session_key that is attached as a request header
	users 				= ArrayField(models.CharField(max_length=255), default=list, blank=True, help_text="session id's of users who are connected to chat room.")


	def __str__(self):
		return self.title


	def connect_user(self, session_id):
		"""
		return true if user is added to the users list
		"""
		is_user_added = False
		if not session_id in self.users:
			self.users.append(session_id)
			self.save()
			is_user_added = True
		return is_user_added 


	def disconnect_user(self, session_id):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		if session_id in self.users:
			self.users.remove(session_id)
			self.save()
			is_user_removed = True
		return is_user_removed 


	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return "room-%s" % self.id


class PublicRoomChatMessageManager(models.Manager):
    def by_room(self, room):
        qs = PublicRoomChatMessage.objects.filter(room=room).order_by("-timestamp")
        return qs

class PublicRoomChatMessage(models.Model):
    """
    Chat message created by a user inside a PublicChatRoom
    """
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room                = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
    timestamp           = models.DateTimeField(auto_now_add=True)
    content             = models.TextField(unique=False, blank=False,)

    objects = PublicRoomChatMessageManager()

    def __str__(self):
        return self.content





























