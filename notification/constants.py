DEFAULT_NOTIFICATION_PAGE_SIZE = 15

"""
"General" notifications include:
	1. FriendRequest
	2. FriendList
"""
GENERAL_MSG_TYPE_NOTIFICATIONS_PAYLOAD = 0  # New 'general' notifications data payload incoming
GENERAL_MSG_TYPE_UPDATED_NOTIFICATION = 5  # Update a notification that has been altered (Ex: Accept/decline a friend request)