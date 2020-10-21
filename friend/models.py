from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from notification.models import Notification
from chat.utils import find_or_create_private_chat


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
				from_user=account,
				redirect_url=f"{settings.BASE_URL}/account/{account.pk}/",
				verb=f"You are now friends with {account.username}.",
				content_type=content_type,
			)
			self.save()

			# Create a private chat (or activate an old one)
			chat = find_or_create_private_chat(self.user, account)
			if not chat.is_active:
				chat.is_active = True
				chat.save()


	def remove_friend(self, account):
		if account in self.friends.all():
			self.friends.remove(account)

			# Deactivate the private chat between these two users
			chat = find_or_create_private_chat(self.user, account)
			if chat.is_active:
				chat.is_active = False
				chat.save()

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
			from_user=self.user,
			redirect_url=f"{settings.BASE_URL}/account/{self.user.pk}/",
			verb=f"You are no longer friends with {self.user.username}.",
			content_type=content_type,
		)

		# Create notification for remover
		self.notifications.create(
			target=self.user,
			from_user=removee,
			redirect_url=f"{settings.BASE_URL}/account/{removee.pk}/",
			verb=f"You are no longer friends with {removee.username}.",
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
		"""
		Update the notification for the person who accepted.
		Create a notification for the person who sent it.
		return the updated notification for person who accepted.
		"""
		receiver_friend_list = FriendList.objects.get(user=self.receiver)
		if receiver_friend_list:

			content_type = ContentType.objects.get_for_model(self)

			# Update notification for RECEIVER
			receiver_notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
			receiver_notification.is_active = False
			receiver_notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
			receiver_notification.verb = f"You accepted {self.sender.username}'s friend request."
			receiver_notification.timestamp = timezone.now()
			receiver_notification.save()

			receiver_friend_list.add_friend(self.sender)
			# receiver_friend_list.save()
			sender_friend_list = FriendList.objects.get(user=self.sender)
			if sender_friend_list:

				# Create notification for SENDER
				self.notifications.create(
					target=self.sender,
					from_user=self.receiver,
					redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
					verb=f"{self.receiver.username} accepted your friend request.",
					content_type=content_type,
				)

				sender_friend_list.add_friend(self.receiver)
				# sender_friend_list.save()
				self.is_active = False
				self.save()
			return receiver_notification
			

	def decline(self):
		"""
		Update the notification for the person who declined.
		Create a notification for the person who sent it.
		return the updated notification for person who declined.
		"""
		self.is_active = False
		self.save()

		content_type = ContentType.objects.get_for_model(self)

		# Update notification for RECEIVER
		notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
		notification.is_active = False
		notification.redirect_url = f"{settings.BASE_URL}/account/{self.sender.pk}/"
		notification.verb = f"You declined {self.sender}'s friend request."
		notification.from_user = self.sender
		notification.timestamp = timezone.now()
		notification.save()

		# Create notification for SENDER
		self.notifications.create(
			target=self.sender,
			verb=f"{self.receiver.username} declined your friend request.",
			from_user=self.receiver,
			redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
			content_type=content_type,
		)

		return notification


	def cancel(self):
		self.is_active = False
		self.save()

		content_type = ContentType.objects.get_for_model(self)

		# Create notification for SENDER
		self.notifications.create(
			target=self.sender,
			verb=f"You cancelled the friend request to {self.receiver.username}.",
			from_user=self.receiver,
			redirect_url=f"{settings.BASE_URL}/account/{self.receiver.pk}/",
			content_type=content_type,
		)

		notification = Notification.objects.get(target=self.receiver, content_type=content_type, object_id=self.id)
		notification.verb = f"{self.sender.username} cancelled the friend request sent to you."
		notification.timestamp = timezone.now()
		notification.read = False
		notification.save()

	@property
	def get_cname(self):
		"""
        For determining what kind of object is associated with a Notification
        """
		return "FriendRequest"


@receiver(post_save, sender=FriendRequest)
def create_notification(sender, instance, created, **kwargs):
	if created:
		instance.notifications.create(
			target=instance.receiver,
			from_user=instance.sender,
			redirect_url=f"{settings.BASE_URL}/account/{instance.sender.pk}/",
			verb=f"{instance.sender.username} sent you a friend request.",
			content_type=instance,
		)

























