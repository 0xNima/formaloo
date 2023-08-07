# Dockerfile

FROM python:3.11.1-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 8000

RUN mkdir /var/log/appstore

COPY . .
