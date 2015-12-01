The Restaurant Menus App
========================

This application manages menus from different restaurants. Authenticated users can
Create, read, update and delete restaurants and their respective menu items. 

All users can read all the info, but only the Restaurant "owner" (i.e, the user 
who created the restaurant) is able to make changes on it.

To run the application:

1. First, create the database, by running:

python database_setup.py

2. As an optional item, you can pre-populate the database with some restaurants, by running:

python lotsofmenuswithuser.py

3. Add your valid google credentials in file client_secrets.json (not adding mine for safety reasons, sorry)

4. Add your valid facebook credentials in file fb_client_secrets.json 

5. To start the application, run:

python finalProject.py

And visit the application at http://localhost:5000
