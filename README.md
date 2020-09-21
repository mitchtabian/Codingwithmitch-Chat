# Django Channels and Sockets Playground
See this project in production: https://open-chat.xyz/


# Important Notes
1. Create at least one user before running
	`python manage.py createsuperuser` or create a regular user using shell: 

	```
	>>> python manage.py shell
	>>> from django.contrib.auth.models import User
	>>> user=User.objects.create_user('Rob', password='password')
	>>> user.save()
	```
1. Must have redis server installed and running and **Redis does not work on windows.** I tried many ways but it turned out to be a pain. **Alternative**: Menurai: https://docs.memurai.com/en/installation.html. Just install and windows will run it as a service.

# Third party libs:
### CDN 
1. Cropper js
   - https://github.com/fengyuanchen/cropperjs
   - CDN: https://cdnjs.com/libraries/markdown-it
1. Highlight.js
   - https://highlightjs.org/usage/
   - CDN: https://cdnjs.com/libraries/highlight.js
1. markdown-it
   - https://github.com/markdown-it/markdown-it
   - CDN: https://cdnjs.com/libraries/markdown-it

### Without CDN
1. Javascript Collections
   - https://www.collectionsjs.com/






