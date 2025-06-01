FROM navikey/raspbian-buster:latest

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install RPi.GPIO
