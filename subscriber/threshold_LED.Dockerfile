FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    python-dev \
    python-rpi.gpio \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install 
