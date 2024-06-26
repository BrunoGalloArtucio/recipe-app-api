FROM python:3.9-alpine3.13
LABEL maintainer="brunogallo"

# Recommended when running python in docker. We don't want to buffer the output
# so that we can see logs immediately
ENV PYTHONBUFFERED 1

# Copy files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt
COPY ./app /app

# Default directory where commands will be run
WORKDIR /app

# PORT
EXPOSE 8000

# Set build argument DEV to false
ARG DEV=false 

# build-base postgresql-dev musl-dev are only needed to install postgresql
# but not to run it, so we create a virtual dependency package and group them
# in the tmp-build-deps folder. Then we delete it once we're done installing
# our dependencies so as to keep our docker image light

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Update PATH environment variable where executables will be run
ENV PATH="/py/bin:$PATH"

# Switch to django-user from root user with full privileges
USER django-user