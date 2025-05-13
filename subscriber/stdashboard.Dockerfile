FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install matplotlib streamlit pandas numpy altair sqlalchemy
RUN mkdir -p /.streamlit/
RUN touch /.streamlit/secrets.toml
EXPOSE 8501
