from django.db import models
from django.conf import settings


class FriendList(models.Model):

	user 				= models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
	friends 			= models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name="friends") 

	def __str__(self):
		return self.user.username

	def add_friend(self, account):
		if not account in self.friends.all():
			self.friends.add(account)

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



class FriendRequest(models.Model):

	sender 				= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender")
	receiver 			= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="receiver")

	def __str__(self):
		return self.sender.username

	def accept(self):
		receiver_friend_list = FriendList.objects.get(user=self.receiver)
		if receiver_friend_list:
			receiver_friend_list.add_friend(self.sender)
			receiver_friend_list.save()
			sender_friend_list = FriendList.objects.get(user=self.sender)
			if sender_friend_list:
				sender_friend_list.add_friend(self.receiver)
				sender_friend_list.save()
		self.delete()
		self.save()








