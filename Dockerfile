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
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

# Update PATH environment variable where executables will be run
ENV PATH="/py/bin:$PATH"

# Switch to django-user from root user with full privileges
USER django-user