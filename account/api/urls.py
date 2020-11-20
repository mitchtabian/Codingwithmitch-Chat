from django.urls import path

from account.api.views import(
	login_view
)

app_name = 'account'

urlpatterns = [
 	path('login', login_view, name="login"), 
]



