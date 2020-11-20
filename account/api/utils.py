from rest_framework.authtoken.models import Token

def generate_new_token(account):
	try:
		token = Token.objects.get(user=account)
		token.delete()
	except Token.DoesNotExist:
		pass
	token = Token.objects.create(user=account)
	return token







