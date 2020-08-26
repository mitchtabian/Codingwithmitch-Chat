from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType



class Notification(models.Model):

	target 						= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	verb 						= models.CharField(max_length=255, unique=False, blank=True, null=True)

	completion_verb 			= models.CharField(max_length=255, unique=False, blank=True,)

	positive_action_object		= models.URLField(max_length=500, null=True, unique=False, blank=True, help_text="The URL to be executed if accepted by the Target (User).")
	
	negative_action_object		= models.URLField(max_length=500, null=True, unique=False, blank=True, help_text="The URL to be executed if declined by the Target (User).")

	timestamp 					= models.DateTimeField(auto_now_add=True)

	# Actor: A generic type that can refer to a FriendRequest, Unread Message, or any other type of "Notification"
	# See article: https://simpleisbetterthancomplex.com/tutorial/2016/10/13/how-to-use-generic-relations.html
	content_type 				= models.ForeignKey(ContentType, on_delete=models.CASCADE)
	object_id 					= models.PositiveIntegerField()
	content_object 				= GenericForeignKey()

	def __str__(self):
		if self.verb == None:
			return self.completion_verb
		return self.verb

	def get_content_object_type(self):
		return str(self.content_object.get_cname)









