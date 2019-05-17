# mikaponics-back
Online aquaponics / hydroponic device monitoring portal implemented in Python and powered by Django.


## Instructions
### Prerequisites
You must have the following applications installed before proceeding. If you are missing any one of these then you cannot begin.

* ``Python 3.7``
* ``virtualenv``
* ``redis``
* ``Postgres 10``

#### Installation
The following section explains how to setup the application.

1. Clone a copy of the project somewhere on your machine, we'll be saving to the following locaiton.

  ```
  mkdir ~/python/github.com/mikaponics;
  cd ~/python/github.com/mikaponics;
  git clone https://github.com/mikaponics/mikaponics-back.git;
  cd mikaponics-back
  ```


2. Setup our virtual environment

  ```
  virtualenv -p python3.7 env
  ```


3. Now lets activate virtual environment

  ```
  source env/bin/activate
  ```


4. Now lets install the libraries this project depends on.

  ```
  pip install -r requirements.txt
  ```

#### Database Setup
This project uses the ``PostGres`` database and as a result requires setup before running. The following instructions are to be run in your ``PostGres`` console:

  ```sql
  drop database mikaponics_db;
  create database mikaponics_db;
  \c mikaponics_db;
  CREATE USER django WITH PASSWORD '123password';
  GRANT ALL PRIVILEGES ON DATABASE mikaponics_db to django;
  ALTER USER django CREATEDB;
  ALTER ROLE django SUPERUSER;
  CREATE EXTENSION postgis;
  ```


#### Environment Variables Setup
1. Populate the environment variables for our project.

  ```
  ./setup_credentials.sh
  ```

2. Go inside the environment variables.

  ```
  vi ./mikaponics/mikaponics/.env
  ```

3. Edit the file to suite your needs.

### Finalization.

1. Run the following. **Please change the password to your own.**

  ```
  python manage.py makemigrations
  python manage.py migrate
  python manage.py init_mikaponics
  python manage.py init_crop_data_sheets
  python manage.py create_admin_user "bart@mikasoftware.com" "123password" "Bart" "Mika";
  python manage.py setup_resource_server_authorization
  ```

2. Register the app with the following social-auth services. Also read [this tutorial](https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html) on setting these up.

    ```
    https://github.com/settings/applications/new
    https://apps.twitter.com/
    https://facebook.com/
    ```

3. If you would like to have some random test data available for your app, feel free to run any of theses.

    ```
    # Smallest dataset
    python manage.py seed_database 1 1 1000

    # Small dataset
    python manage.py seed_database 5 10 2500

    # Medium dataset
    python manage.py seed_database 25 20 5000

    # Large dataset
    python manage.py seed_database 100 30 10000

    # Gigantic dataset
    python manage.py seed_database 10000 50 100000

    # Epic dataset
    python manage.py seed_database 100000 75 1000000
    ```

4. If you would like to have some random test data to a specific user, feel free to run:

    ```
    python manage.py seed_user "bart@mikasoftware.com" 1 5000
    ```
