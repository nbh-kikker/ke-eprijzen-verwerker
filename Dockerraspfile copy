#**************************************
# Build By:
# https://itheo.tech 2024
# MIT License
# Dockerfile to run the python script
#**************************************

FROM python:3.11-slim-bookworm as base

LABEL org.opencontainers.image.authors="info@itheo.tech"
ENV TZ=Europe/Amsterdam
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
    apt-utils \
    tzdata \
    locales \
    python3-dev \
    cmake \
    g++ \
    gcc \
    libxml2-dev \
    libxslt-dev \
    build-essential \
    docker-compose && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get -y autoremove

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# nl_NL.UTF-8 UTF-8/nl_NL.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

RUN pip install --upgrade pip

WORKDIR /src

COPY requirements.txt .
COPY ./src .

RUN pip install -r requirements.txt --no-cache-dir

FROM base as dev
ENV PY_ENV=dev
CMD [ "python", "main.py" ]

FROM base as acc
ENV PY_ENV=acc
CMD [ "python", "main.py" ]

FROM base as PROD
ENV PY_ENV=prod
CMD [ "python", "main.py" ]
