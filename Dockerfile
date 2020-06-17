# Base Image for dev version with SQLLITE
FROM python:3.7

MAINTAINER Umesh Saruk

# set default environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV LANG C.UTF-8
ENV DJANGO_SETTINGS_MODULE=config.settings


# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        python3-setuptools \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# create and set working directory
RUN mkdir /app
WORKDIR /app


# install environment dependencies
RUN pip3 install --upgrade pip
RUN pip3 install psycopg2 pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --ignore-pipfile

# copy docker-entrypoint.sh
COPY ./docker-entrypoint.sh ./docker-entrypoint.sh

# Add current directory code to working directory
ADD . .
EXPOSE 8000

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]


