# Lets Do It Now Challenge: Blogs

This is the documentation for the installation and testing of the Blog Platform challenge proposed.

## Getting Started

In this section you can find the configurations you need to install and set the app for the future and correct usage. Here is the step by step:

* Create and activate a Python virtual environment
* Install the dependencies you can find in the requirements.txt file
* Create a .env file in the root directory and fill the information of your local PostgreSQL database. *Note:* I shared the Django Key through email
* Move to the blog app using the command ```cd blog```
* Run the command ```python manage.py migrate``` and check that the database is configured correctly. *Note:* Use pgAdmin4 to help you here
* Create a superuser so you can use the Django Admin Portal
* Run the server with ```python manage.py runserver```

## Endpoints documentation

You have all the endpoints available, you can check them in the server you just launch. Anyways, you can also go to 127.0.0.1:8000/api/schema/swagger/ to check a Swagger Documentation. But, this is not just for the endpoints documentation, you can test those endpoints and check the available functionalities:

* health-check: Check if the API is up and running
* signup: Register new user
* login: Login a user
* logout: Exit user¨
* refresh_token: JWT implementation for authentication
* user CRUD: Read, update and delete user
* profile CRUD: Create, read, update and delete profile
* post, comment, like CRUD...

## Good practices and tests

* I used pytest for testing some endpoints. Command: ```pytest```
* I used flake8 for good practices coding. Command: ```flake8```
* I used isort to organize the imports. Command: ```isort .```

## Considerations

Due to the deadline, I couldn't finish implementating all the prototype completely. But, I managed to deliver a strong prototype covering most of the challenge requirements. For example, we just have a few tests and we should have more than that. The base for the permissions were settled, but not implemented at all. Anyways, the prototype is good.