# Login

### Request
**POST** `https://open-chat.xyz/api/account/login`

**form-data**
| key 			| value				|
| ------------- | ------------------|
| `username`	| `<your email>`	|
| `password`	| `<your password>`	|


### Responses

#### Success
```
{
	"response_code": "Success",
	"token": "da19fcbc2b60684d26e76f3a9c64dd23cfc115d7",
	"account_id": 1
}
```

#### Error

##### Invalid credentials
```
{
	"response_code": "Error",
	"login_response": "Invalid credentials"
}
```

##### Email does not exist on servers
```
{
	"response_code": "Error",
	"login_response": "That account does not exist on our servers"
}
```

##### Incorrect password
```
{		
	"response_code": "Error",
	"login_response": "Incorrect password"
}
```


































