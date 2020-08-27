from django.urls import path

from notification.views import(
	get_notifications,
	refresh_notifications,
)

app_name = 'notification'

urlpatterns = [
    path('get_notifications/', get_notifications, name='get-notifications'),
    path('refresh_notifications/', refresh_notifications, name='refresh-notifications'),
]

