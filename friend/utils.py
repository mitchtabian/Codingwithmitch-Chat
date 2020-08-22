from friend.models import FriendRequest


def get_friend_request_or_false(sender, receiver):
	try:
		return FriendRequest.objects.get(sender=sender, receiver=receiver)
	except FriendRequest.DoesNotExist:
		return False



