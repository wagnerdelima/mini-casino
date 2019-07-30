## Mini Casino 

### Running the Project with Django

You need to create a database (MySQL) and set it onto the `mini_casino.settings.py` file.
There are environment variables set in the DATABASE section,
you may overwrite them and proceed.

In order to run the project do the following below.


Running with django only
Once database is set, run migrations:

    $ python manage.py migrate

Create a virtual environment and activate with:
    
    $ virtualenv venv
    $ source venv/bin/activate
    
Install the requirements with and run:
    
    $ pip install -r requirements.txt
    $ python manage.py runserver

### Running with Docker
This is the smart way of running the project. Leave the `mini_casino.settings DATABASE`
section untouched.


Run with

    $ docker-compose up -d --build
    
Run migrations with (wait few seconds for database creation)

    $ docker-compose exec app python manage.py migrate
 