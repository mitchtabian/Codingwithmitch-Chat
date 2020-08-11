# Django Channels and Sockets Playground
Playing around with channels and sockets for django. 

I *might* create a realtime chat app for codingwithmitch.com and build an android app to interact with it via sockets.



## Important Notes
1. Create at least one user before running
	`python manage.py createsuperuser` or create a regular user using shell: 

	```
	python manage.py shell
	.>> from django.contrib.auth.models import User
	>>> user=User.objects.create_user('Rob', password='password')
	>>> user.save()
	```
1. Must have redis server installed and running and **Redis does not work on windows.** I tried many ways but it turned out to be a pain. **Alternative**: Menurai: https://docs.memurai.com/en/installation.html. Just install and windows will run it as a service.









