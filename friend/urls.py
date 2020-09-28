from django.urls import path

from friend.views import(
	send_friend_request,
	friend_requests,
)

app_name = 'friend'

urlpatterns = [
    path('friend_request/', send_friend_request, name='friend-request'),
    path('friend_requests/<user_id>/', friend_requests, name='friend-requests'),
]