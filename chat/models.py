from django.db import models
from django.conf import settings




class PrivateChatRoom(models.Model):
	"""
	A private room for people to chat in.
	"""
	user1               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user1")
	user2               = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user2")

	@property
	def group_name(self):
		"""
		Returns the Channels Group name that sockets should subscribe to to get sent
		messages as they are generated.
		"""
		return f"PrivateChatRoom-{self.id}"


class RoomChatMessageManager(models.Manager):
	def by_room(self, room):
		qs = RoomChatMessage.objects.filter(room=room).order_by("-timestamp")
		return qs

class RoomChatMessage(models.Model):
	"""
	Chat message created by a user inside a Room
	"""
	user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	room                = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
	timestamp           = models.DateTimeField(auto_now_add=True)
	content             = models.TextField(unique=False, blank=False,)

	objects = RoomChatMessageManager()

	def __str__(self):
		return self.content





