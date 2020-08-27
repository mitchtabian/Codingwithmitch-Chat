from django.urls import path

from notification.views import(
	get_notifications,
)

app_name = 'notification'

urlpatterns = [
    path('get_notifications/', get_notifications, name='get-notifications'),
]

