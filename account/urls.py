from django.urls import path

from account.views import (
	account_view,
)

app_name = 'account'

urlpatterns = [
	path('<user_id>/', account_view, name="view"),
]