# Formaloo Appstore
Extensive service for publishing and purchasing apps.

Powered by Django and DRF.

## Build instructions for Docker (recommended)
### Clone source code
    git clone https://github.com/0xNima/formaloo.git

### Rename `.env-template`
    cd formaloo/

    mv .env-template .env
    
Rename `.env-template` file to `.env` and fill the variables with proper values
    
    SERVICE_PORT=8000   # service will run in this port.

    SUPERUSER_USERNAME=admin   # superuser username which will be created automatically

    SUPERUSER_PASSWORD=admin   # superuser password which will be created automatically

    PRODUCTION=No    # No: development environment, Yes: production

    LITE_DB=No    # set Yes if you want to use SQLite instead of Postgres. Note: this will be ignored in production

    DB_NAME=appstore

    DB_USER=postgres

    DB_PASS=password
  
    DB_HOST=localhost    # this will be override by docker-compose

    DB_PORT=5432

    DJANGO_SECRET_KEY=put-an-super-secure-secret-here    # put a secure key here

### Start the project
    docker-compose up -d
    
### Logs
All logs exist in `./logs` folder.

## Build instructions without Docker
### Clone source code
    git clone https://github.com/0xNima/formaloo.git

### Rename `.env-template`
    cd formaloo/

    mv .env-template .env

change environment variables with appropriate values. You can see above for detail of each variable.

### Create Virtualenv and install prerequisite
    python3 -m venv venv

    source venv/bin/activate

    pip install -r requirements.txt

### Run tests
    python manage.py test apps

### Create db and Run migrations
    python manage.py create_db && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py create_superuser && \
    python manage.py collectstatic --noinput && \
    python manage.py runserver

## Documentations
Navigate to http://localhost:8000/api/redoc/ to see the full documentation of API.

## Integration with Dashboard service
Appstore can be integrated with any dashboard service for monitoring purposes. For decoupling this process from our system, we implemented an event-driven architecture. Appstore will publish metrics as JSON payloads through the event queues. On the other side, the Dashboard service will consume and use these events.

![Recommended Design](formaloo.drawio.png)
