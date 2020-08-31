"""
"General" notifications include:
	1. FriendRequest
	2. FriendList
"""
GENERAL_MSG_TYPE_NOTIFICATIONS_PAYLOAD = 0  # New 'general' notifications data payload incoming
GENERAL_MSG_TYPE_PAGINATION_EXHAUSTED = 1  # No more 'general' notifications to retrieve
GENERAL_MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD = 2  # Retrieved all 'general' notifications newer than the oldest visible on screen



"""
"Chat" notifications include:
	1. UnreadChatRoomMessages
"""
CHAT_MSG_TYPE_NOTIFICATIONS_PAYLOAD = 10  # New 'chat' notifications data payload incoming
CHAT_MSG_TYPE_PAGINATION_EXHAUSTED = 11  # No more 'chat' notifications to retrieve
CHAT_MSG_TYPE_NOTIFICATIONS_REFRESH_PAYLOAD = 12  # Retrieved all 'chat' notifications newer than the oldest visible on screen









