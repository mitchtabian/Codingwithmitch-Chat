from django.urls import path

from friend.views import(
	send_friend_request,
	cancel_friend_request,
	remove_friend,
	accept_friend_request,
	decline_friend_request,
	friends_list_view,
	# is_mutual_friend,
)

app_name = 'friend'

urlpatterns = [
    # path('is_mutual_friend/', is_mutual_friend, name='is-mutual-friend'),
    path('list/<username>', friends_list_view, name='list'),
    path('friend_remove/', remove_friend, name='remove-friend'),
    path('friend_request/', send_friend_request, name='friend-request'),
    path('friend_request_cancel/', cancel_friend_request, name='friend-request-cancel'),
    path('friend_request_accept/', accept_friend_request, name='friend-request-accept'),
    path('friend_request_decline/', decline_friend_request, name='friend-request-decline'),
]

