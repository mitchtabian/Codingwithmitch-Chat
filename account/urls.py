from django.urls import path

from account.views import (
	crop_image,
	account_view,
	edit_account_view,
)

app_name = 'account'

urlpatterns = [
	path('<username>/', account_view, name="view"),
	path('<username>/edit/', edit_account_view, name="edit"),
	path('<username>/edit/cropImage/', crop_image, name="crop_image"),
]
