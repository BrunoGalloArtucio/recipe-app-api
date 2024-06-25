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
-   Fixing race condition on app vs db by creating custom Django management command (`app/core/management/commands/wait_for_db.py`). depends-on awaits for the service to start, but not for its application to start. This means that the app service will wait for the db-service to start, but postgresql may not yet be ready to accept connections. Command can be manually run using `docker-compose run --rm app sh -c "python manage.py wait_for_db"`. This command is called in docker-compose and on the checks.yml workflow.
-   Tests with mocks: app/core/tests/test_commands.py
-   Define custom user model to use instead of using the default django admin one so that it's easier to customize in the future (`app/core/models.py`). This is then configured in `settings.py` using `AUTH_USER_MODEL`. A common error when using a custom model is running a migration prior to defining it. To fix this, we need to clear the existing volume using `docker volume ls` to get the volume's name and then `docker volume rm <volume_name>`
-   Testing exception is thrown: `app/core/tests/test_models.py`
-   Add users to admin page: `app/core/admin.py`. This can be checked in `http://127.0.0.1:8000/admin`, after running `docker-compose up`
-   Test admin page: `app/core/tests/test_admin.py`
-   Automatically generate API Documentation using DRF (Django REST Framework) module `drf-spectacular`. First, we configured `drf_spectacular` in `INSTALLED_APPS` and `REST_FRAMEWORK` in `app/app/settings.py`. Then we enabled the doc URLs in `app/app/urls.py`
-   API tests for user API: `app/user/tests/test_user_api.py`
-   Use model serializers to validate and save data to our User Model: `app/user/serializers.py`
-   Use `rest_framework` for create user API. User URls are defined in `app/user/urls.py` and then registered in `app/app/urls.py`. URLs use views which are defined in `app/user/views.py`. Views will determine which method will be available in each URL. Finally, views use serializers located in `app/user/serializers.py` to update the entities in the database.
