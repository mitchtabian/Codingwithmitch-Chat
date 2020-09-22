# Django Channels and Sockets Playground
See this project in production: https://open-chat.xyz/


# Important Notes
1. See **Getting Started Guide** below for how to set this project up on windows.
1. Create at least one user before running
	`python manage.py createsuperuser` or create a regular user using shell: 

	```
	>>> python manage.py shell
	>>> from django.contrib.auth.models import User
	>>> user=User.objects.create_user('Rob', password='password')
	>>> user.save()
	```
1. Must have redis server installed and running and **Redis does not work on windows.** I tried many ways but it turned out to be a pain. **Alternative**: Menurai: https://docs.memurai.com/en/installation.html. Just install and windows will run it as a service.


# Getting Started Guide 
A guide to creating a new django project that uses:
1. windows
1. python3.8.2
1. pip
1. django 2.2.15 (LTS)
1. virtualenv
1. Redis
1. django channels 2
1. Postgres

## Install Python3.8.2
Bottom of page: https://www.python.org/downloads/release/python-382/

## Installing pip
1. https://pypi.org/project/pip/
1. Open cmd prompt
1. `pip install pip`

## Setup virtualenv
1. Navigate to where you want to keep your django projects. I use `D://DjangoProjects/`
1. Create `D://DjangoProjects/ChatServerPlayground` folder or whatever you want to name the project.
1. Create a virtual environment to run the project in.
	- Typically I call it "venv" but you can call it something else if you like. Doesn't matter. djangoproject_venv for example.
	- `python -m venv venv` or `python -m venv djangoproject_venv` if you like
1. Open a cmd prompt in your project directly
1. Navigate into `venv` folder
	- `cd venv`
1. Activate the virtual environment
	- **Windows**: `Scripts\activate` 
	- **Linux**: `source bin/activate`
	- **Mac (I think)**: `source bin/activate`


## Install Django and create Django project
1. Install django 
	- `python -m pip install Django==2.2.15`
	- See LTS: https://www.djangoproject.com/download/
1. Create the django project
	- `django-admin startproject ChatServerPlayground`
1. Rename root directory (`ChatServerPlayground`) to `src`
	- I prefer to name my root directory `src` because inside the project is another folder named `ChatServerPlayground` or whatever you called your project
	- So now you should have the following folder structure:
		- `D://DjangoProjects/ChatServerPlayground/venv/src/`
			- Inside `src` you will have a folder name `ChatServerPlayground` and a `manage.py` file
1. Keep track of the libraries you use
	- `pip freeze > requirements.txt`
1. Run the server to make sure it's working
	- `python manage.py runserver`
1. Visit `http://127.0.0.1:8000/`


## Postgres Setup (Windows)
Postgres needs to run as a service on your machine. Since I'm using windows I will show you how to do this on windows. When we launch this website in production at the end of the course I'll show you how to setup postgres on Linux.
1. Download postgres: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
	- I am using x86-64 version 10 for windows
1. run the `.exe` file and go through the installation
	1. **remember the superuser password you use.** This is very important.
	1. port 5432 is the standard
1. After installation confirm the service is running by opening the "Services" window on windows.
	- If it's not running then start it
1. Confirm you have access to database
	1. open cmd prompt
	1. write `psql postgres postgres`
		- means: "connect to the database named 'postgres' with the user 'postgres'". 'postgres' is the default root user name for the database.
1. Some commands you'll find useful:
	1. List databases
		- `\l`
	1. Connect to a different database
		- `\c codingwithmitch_chat`
		- **Keep in mind** you will not have any other databases. We will create one in a second.
	1. List the tables in a database
		`\dt`
	1. create a new database for our project
		- `CREATE DATABASE codingwithmitch_chat_dev;`
	1. Create a new user that has permissions to use that database
		- `CREATE USER django WITH PASSWORD 'password';`
		- These credentials are important to remember because they are used in the django postgres configuration.
	1. List all users
		- `/du`
	1. Give the new user all privileges on new db
		- `GRANT ALL PRIVILEGES ON DATABASE codingwithmitch_chat_dev TO django;`
	1. Test
		1. disconnect from db
			- `\q`
		1. Connect to the db with user
			- `psql codingwithmitch_chat_dev django`


## Django and Postgres Setup
1. Install `psycopg2`
	- `pip install psycopg2`
1. Add to requirements
	- `pip freeze > requirements.txt`
1. Update `settings.py` with the following postgres configuration
	```
	DB_NAME = "codingwithmitch_chat_dev"
	DB_USER = "django"
	DB_PASSWORD = "password"
	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.postgresql_psycopg2',
	        'NAME': DB_NAME,
	        'USER': DB_USER,
	        'PASSWORD': DB_PASSWORD,
	        'HOST': 'localhost',
	        'PORT': '5432',
	    }
	}
	```
1. Delete the sqlite database in project root
1. migrate to commit changes to database
	- `python manage.py migrate`
1. create a superuser
	- `python manage.py createsuperuser`
1. log into admin
	- `python manage.py runserver`
	- visit `http://127.0.0.1:8000/admin`
	- This confirms the database is working correctly.


## Install Redis (Required for Django Channels)

TODO: continue...



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











