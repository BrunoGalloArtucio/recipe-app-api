# recipe-app-api

Recipes API

### Items

-   Configure .gitignore to ignore pycached files
-   Configure docker using Dockerfile
-   Configure docker-compose.yml file to be able to access our docker server via docker-compose:

    -   Build docker image: `docker-compose build`.
    -   Tear down docker server: `docker-compose down`.
    -   Set up docker server: `docker-compose up`.
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
-   Models created in file `app/core/models.py`. These models are directly mapped to the DB by the ORM so every time a model is created/updated/deleted, the migration files must be generated using `docker-compose run --rm app sh -c "python manage.py makemigrations"`. These migrations are then automatically executed when building the app (check `docker-compose.yml` -> `services.app.build.command`).
-   Models are then registered in the `app/core/admin.py` in order to be accessible through admin page.
-   Use model serializers to validate and save data to our User Model: `app/user/serializers.py`
-   Use `rest_framework` for create user API. User URls are defined in `app/user/urls.py` and then registered in `app/app/urls.py`. URLs use views which are defined in `app/user/views.py`. Views will determine which method will be available in each URL. Finally, views use serializers located in `app/user/serializers.py` to update the entities in the database.
-   A view is what handles a request made to a URL.
-   Django uses python functions that accept a single request argument, and that can be used as the view to handle a particular request to a URL.
-   DRF uses classes that provides engs with reusable logic while allowing them to override behavior for customization. DRF also support function based views using decorators. APIView and Viewsets are DRF base classes:

    -   APIView: focused around HTTP method. There's a specific class method available for all of the different HTTP methods you want to support in that endpoint (HTTP methods in lower case). They are mostly useful for non CRUD APIs, like running jobs.
    -   Viewsets: they're focused around actions, so the naming of the functions include names like retrieve, list, update, partial update, and destroy. Usually a viewset will map specifically to a model in your system. With viewsets, Routers can be used to automatically generate URLs. Viewsets are ideal for CRUD operation on a particular models.

-   Recipe app includes a CRUD oriented API following the same pattern as users (serializer, view, urls). This API uses one serializer for the list (omits description field), and another one for the rest of the endpoints.
-   The create method is overriden for `RecipeSerializer` in `app/recipe/serializers.py` so as to create the tags included in with the recipe if they don't exist, and then saved in the recipe
-   Recipe model includes manyToMany relations
-   In the `app/recipe/views.py` file, the `mixins.UpdateModelMixin`, `mixins.DestroyModelMixin`, and `mixins.ListModelMixin` are responsible for enabling PUT/PATCH, DELETE, and GET methods
-   Media and static files are files not generated by Python code. They include things such as Images, css, javascript, or icons that may be needed to your project. There are two types:

    -   Media: uploaded at runtime (eg: user uploads)
    -   Static: generated on build

-   In this course we use indirectly when uses things like django admin. This can be seen when browsing the admin page, in the style of elements..
-   In order to use static and media files directly with Django, we have to add some config to `app/app/settings.py`:

    -   `STATIC_URL`: Base static URL (`/static/static`)
    -   `MEDIA_URL`: Base media URL (`/static/media`)
    -   `MEDIA_ROOT`: Root directory on the server (`/vol/web/media`)
    -   `STATIC_ROOT`: Root directory on the server (`/vol/web/static`)

-   Files will be stored in another docker volume: `/vol/web`. Static and media files will be stored in subdirectories of this volume.
-   There's a difference regarding media and static files between running Django in development and production mode. When we use development mode, we use django development server which is designed to serve the static files in an easier way. For static file URLs, the django development server maps the URLs apps to the `static` folders in each app. For media URLs, the django development server retrieves the files directly from the media root.

    -   `GET /static/static/admin/style.css` <- Django Dev Server <- `[admin]/static/style.css`
    -   `GET /static/media/recipe/123.jpeg` <- `/vol/static/media/file.jpeg`

-   For a deployed application, a reverse proxy is used:

    -   `GET /static/...` <- Reverse proxy <- `/vol/web/...`
    -   `GET /static/media/file.jpeg` <- `/vol/web/media/file.jpeg`
    -   `GET /static/static/admin/style.css` <- `/vol/web/static/admin/style.css`

-   In order to gather up all static files for all of the apps in the project, we use the `python manage.py collectstatic` command. This puts all the static files for all the apps in the `STATIC_ROOT`.
-   We configure static/media URLs to behave differently in development vs prod in `app/app/urls.py`
-   `SPECTACULAR_SETTINGS` is set in `settings.py` to ease file upload
-   Adding query string parameter documentation and filtering by tags/ingredients (many-to-many) done in `RecipeViewSet.get_query_set` of `app/recipe/views.py`
-   Added filtering tags/ingredients by assignation to recipes done in `BaseRecipeAttrViewSet.get_query_set` of `app/recipe/views.py`
