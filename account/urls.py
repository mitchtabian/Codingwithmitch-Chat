from django.urls import path

from account.views import (
	account_view,
	login_view,
	register_view,
	logout_view,
)

app_name = 'account'

urlpatterns = [
	path('', account_view, name="account"),
	path('login/', login_view, name="login"),
	path('logout/', logout_view, name="logout"),
	path('register/', register_view, name="register"),
]
