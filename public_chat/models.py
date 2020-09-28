from django.db import models
from django.conf import settings


class PublicChatRoom(models.Model):

	# Room title
	title 				= models.CharField(max_length=255, unique=True, blank=False,)

	# all users who are authenticated and viewing the chat
	users 				= models.ManyToManyField(settings.AUTH_USER_MODEL, help_text="users who are connected to chat room.", blank=True, null=True)

	def __str__(self):
		return self.title


	def connect_user(self, user):
		"""
		return true if user is added to the users list
		"""
		is_user_added = False
		if not user in self.users.all():
			self.users.add(user)
			self.save()
			is_user_added = True
		elif user in self.users.all():
			is_user_added = True
		return is_user_added 


	def disconnect_user(self, user):
		"""
		return true if user is removed from the users list
		"""
		is_user_removed = False
		if user in self.users.all():
			self.users.remove(user)
			self.save()
			is_user_removed = True
		return is_user_removed 


	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return "PublicChatRoom-%s" % self.id


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

















