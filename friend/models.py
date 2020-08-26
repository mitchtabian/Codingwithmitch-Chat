from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from notification.models import Notification



class FriendList(models.Model):

	user 				= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
	friends 			= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends") 

	notifications		= GenericRelation(Notification)

	def __str__(self):
		return self.user.username

	def add_friend(self, account):
		if not account in self.friends.all():
			self.friends.add(account)

			content_type = ContentType.objects.get_for_model(self)

			# Create notification
			self.notifications.create(
				target=self.user,
				verb=None,
				completion_verb=f"You are now friends with {account.username}.",
				positive_action_object=None,
				negative_action_object=None,
				content_type=content_type,
			)

	def remove_friend(self, account):
		if account in self.friends.all():
			self.friends.remove(account)

	def unfriend(self, removee):
		remover_friends_list = self # person terminating the friendship

		# Remove friend from remover friend list
		remover_friends_list.remove_friend(removee)

		# Remove friend from removee friend list
		friends_list = FriendList.objects.get(user=removee)
		friends_list.remove_friend(remover_friends_list.user)

		content_type = ContentType.objects.get_for_model(self)

		# Create notification for removee
		friends_list.notifications.create(
			target=removee,
			verb=None,
			completion_verb=f"You are no longer friends with {self.user.username}.",
			positive_action_object=None,
			negative_action_object=None,
			content_type=content_type,
		)

		# Create notification for remover
		self.notifications.create(
			target=self.user,
			verb=None,
			completion_verb=f"You are no longer friends with {removee.username}.",
			positive_action_object=None,
			negative_action_object=None,
			content_type=content_type,
		)

	@property
	def get_cname(self):
		"""
        For determining what kind of object is associated with a Notification
        """
		return "FriendList"

	def is_mutual_friend(self, friend):
		if friend in self.friends.all():
			return True
		return False


class FriendRequest(models.Model):

	sender 				= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
	receiver 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")

	is_active			= models.BooleanField(blank=False, null=False, default=True)

	# Pending friend requests as a notification
	notifications		= GenericRelation(Notification)

	timestamp 			= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.sender.username

	def accept(self):
		receiver_friend_list = FriendList.objects.get(user=self.receiver)
		if receiver_friend_list:

			content_type = ContentType.objects.get_for_model(self)

			# Update notification for RECEIVER
			receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
			receiver_notification.is_active = False
			receiver_notification.positive_action_object = None
			receiver_notification.negative_action_object = None
			receiver_notification.completion_verb = f"You accepted {self.sender.username}'s friend request."
			receiver_notification.save()

			receiver_friend_list.add_friend(self.sender)
			receiver_friend_list.save()
			sender_friend_list = FriendList.objects.get(user=self.sender)
			if sender_friend_list:

				# Create notification for SENDER
				self.notifications.create(
					target=self.sender,
					verb=None,
					completion_verb=f"{self.receiver.username} accepted your friend request.",
					positive_action_object=None,
					negative_action_object=None,
					content_type=content_type,
				)

				sender_friend_list.add_friend(self.receiver)
				sender_friend_list.save()
				self.is_active = False
				self.save()
			

	def decline(self):
		self.is_active = False
		self.save()

		content_type = ContentType.objects.get_for_model(self)

		# Update notification for RECEIVER
		notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
		notification.is_active = False
		notification.positive_action_object = None
		notification.negative_action_object = None
		notification.completion_verb = f"You declined {self.sender}'s friend request."
		notification.save()

		# Create notification for SENDER
		self.notifications.create(
			target=self.sender,
			verb=None,
			completion_verb=f"{self.receiver.username} declined your friend request.",
			positive_action_object=None,
			negative_action_object=None,
			content_type=content_type,
		)


	def cancel(self):
		self.is_active = False
		self.save()

		content_type = ContentType.objects.get_for_model(self)

		# Create notification for SENDER
		self.notifications.create(
			target=self.sender,
			verb=None,
			completion_verb=f"You cancelled the friend request to {self.receiver.username}.",
			positive_action_object=None,
			negative_action_object=None,
			content_type=content_type,
		)

		# find the notification sent to the RECEIVER and delete it
		notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
		notification.delete()

	@property
	def get_cname(self):
		"""
        For determining what kind of object is associated with a Notification
        """
		return "FriendRequest"


@receiver(post_save, sender=FriendRequest)
def create_notification(sender, instance, created, **kwargs):
	if created:
		positive_action_object = settings.BASE_URL + "/friend/friend_request_accept/" + str(instance.pk) + "/"
		negative_action_object = settings.BASE_URL + "/friend/friend_request_decline/" + str(instance.pk) + "/"
		instance.notifications.create(
			target=instance.receiver,
			verb=f"{instance.sender.username} sent you a friend request.",
			positive_action_object=positive_action_object,
			negative_action_object=negative_action_object,
			content_type=instance,
		)

























