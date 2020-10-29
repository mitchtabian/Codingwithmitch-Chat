from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



class Notification(models.Model):

	# Who the notification is sent to
	target 						= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	# The user that the creation of the notification was triggered by.
	from_user 					= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="from_user")

	redirect_url				= models.URLField(max_length=500, null=True, unique=False, blank=True, help_text="The URL to be visited when a notification is clicked.")

	# statement describing the notification (ex: "Mitch sent you a friend request")
	verb 						= models.CharField(max_length=255, unique=False, blank=True, null=True)

	# When the notification was created/updated
	timestamp 					= models.DateTimeField(auto_now_add=True)

	# Some notifications can be marked as "read". (I used "read" instead of "active". I think its more appropriate)
	read 						= models.BooleanField(default=False)

	# A generic type that can refer to a FriendRequest, Unread Message, or any other type of "Notification"
	# See article: https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html
	content_type 				= models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id 					= models.PositiveIntegerField()
	content_object 				= GenericForeignKey()

	def __str__(self):
		return self.verb

	def get_content_object_type(self):
		return str(self.content_object.get_cname)



