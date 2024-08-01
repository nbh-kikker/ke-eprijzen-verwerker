#**************************************
# Build By:
# https://itheo.tech 2024
# MIT License
# Dockerfile to run the python script
#**************************************

# Base stage for building
# FROM python:3.12-slim-bookworm as base
# Use pixi as the base image
FROM ghcr.io/prefix-dev/pixi:0.18.0

# Use debian:bookworm as the second stage base image
FROM debian:bookworm as bookworm

LABEL org.opencontainers.image.authors="info@itheo.tech"
ENV TZ=Europe/Amsterdam
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y \
    apt-utils \
    tzdata \
    locales \
    libstdc++6 \
    && apt-get clean && \
    apt-get -y autoremove

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_GB.UTF-8 UTF-8/en_GB.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# nl_NL.UTF-8 UTF-8/nl_NL.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# de_DE.UTF-8 UTF-8/de_DE.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

# Download and install pixi manually
RUN curl -fsSL https://pixi.sh/install.sh | bash

# Add pixi to the PATH
ENV PATH="/root/.pixi/bin:$PATH"

# Install Python dependencies
WORKDIR /src
COPY pixi.lock .
COPY pixi.toml .

# Copy the source code
COPY ./src .
RUN pixi install

# Development build
FROM base as dev
ENV PY_ENV=dev
CMD ["python", "main.py"]

# Acceptance build
FROM base as acc
ENV PY_ENV=acc
CMD ["python", "main.py"]

# Production build
FROM base as prod
ENV PY_ENV=prod
CMD ["pixi", "run", "python", "main.py"]
