from enum import Enum

class ApiResponseCode(Enum):
	KEY = "response_code"
	SUCCESS = "Success"
	ERROR = "Error"

class ApiLoginResponse(Enum):
	KEY = "login_response"
	INVALID_CREDENTIALS = "Invalid credentials"
	ACCOUNT_DOES_NOT_EXIST = "That account does not exist on our servers"
	INCORRECT_PASSWORD = "Incorrect password"






