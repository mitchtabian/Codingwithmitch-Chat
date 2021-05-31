from django.contrib.auth import authenticate

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view

from account.models import Account
from account.api.constants import ApiResponseCode, ApiLoginResponse
from account.api.utils import generate_new_token



@api_view(['POST', ])
def login_view(request):
	"""
	Attempt a login via rest framework. 
	See [/account/api/documentation.md] for more information.
	"""
	if request.method == 'POST':
		context = {}
		email = request.POST.get('username')
		password = request.POST.get('password')

		if email == "" or password == "":
			context[ApiResponseCode.KEY.value] = ApiResponseCode.ERROR.value
			context[ApiLoginResponse.KEY.value] = ApiLoginResponse.INVALID_CREDENTIALS.value
			return Response(context)

		try:
			account = Account.objects.get(email=email)
		except Account.DoesNotExist:
			context[ApiResponseCode.KEY.value] = ApiResponseCode.ERROR.value
			context[ApiLoginResponse.KEY.value] = ApiLoginResponse.ACCOUNT_DOES_NOT_EXIST.value
			return Response(context)

		account = authenticate(email=email, password=password)
		if account:
			token = generate_new_token(account)
			context[ApiResponseCode.KEY.value] = ApiResponseCode.SUCCESS.value
			context["token"] = token.key
			context["account_id"] = account.id
		else:
			context[ApiResponseCode.KEY.value] = ApiResponseCode.ERROR.value
			context[ApiLoginResponse.KEY.value] = ApiLoginResponse.INCORRECT_PASSWORD.value
		return Response(context)
















