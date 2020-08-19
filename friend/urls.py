from django.urls import path

from friend.views import(
	send_friend_request,
	cancel_friend_request,
	remove_friend,
)

app_name = 'friend'

urlpatterns = [
    path('friend_request/<user_id>/', send_friend_request, name='friend-request'),
    path('friend_request_cancel/<user_id>/', cancel_friend_request, name='friend-request-cancel'),
    path('friend_remove/<user_id>/', remove_friend, name='remove-friend'),
]

