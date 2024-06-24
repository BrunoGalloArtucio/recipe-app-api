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
