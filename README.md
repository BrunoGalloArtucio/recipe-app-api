# recipe-app-api

Recipes API

### Items

-   Configure .gitignore to ignore pycached files
-   Configure docker using Dockerfile
-   Configure docker-compose.yml file to be able to access our docker server via docker-compose:

    -   Build docker image: `docker-compose build`.
    -   Run python commands: `docker-compose run --rm app sh -c "python manage.py <command>"`.
    -   Run server using `docker-compose up`

-   Configure linting tool flake8
-   Configure Checks (Test and Lint) github workflow: .github/workflows/checks.yml. This gets automatically picked up by github. No need to create anything on Github
-   Configure Postgresql in docker-compose.yml, installing dependencies in Dockerfile, and in settings.py DATABASES
-   Create new app using `docker-compose run --rm app sh -c "python manage.py startapp core"` and add it to `settings.py` INSTALLED_APPS
-   Fixing race condition on app vs db by creating custom Django management command (`app/core/management/commands/wait_for_db.py`). depends-on awaits for the service to start, but not for its application to start. This means that the app service will wait for the db-service to start, but postgresql may not yet be ready to accept connections. Command can be manually run using `docker-compose run --rm app sh -c "python manage.py wait_for_db"`
-   Tests with mocks: app/core/tests/test_commands.py
