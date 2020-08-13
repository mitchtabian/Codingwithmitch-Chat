from django.urls import path

from account.views import (
	crop_image,
	account_view,
	edit_account_view,
	login_view,
	register_view,
	logout_view,
)

app_name = 'account'

urlpatterns = [
	path('<username>/', account_view, name="account"),
	path('<username>/edit/', edit_account_view, name="edit_account"),
	path('<username>/edit/cropImage/', crop_image, name="crop_image"),
	path('login/', login_view, name="login"),
	path('logout/', logout_view, name="logout"),
	path('register/', register_view, name="register"),
	
]
