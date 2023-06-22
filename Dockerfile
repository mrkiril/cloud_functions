FROM python:3.11-slim

WORKDIR /app

ARG PIP_REQUIREMENTS_FILE=requirements/test.txt
COPY requirements requirements
RUN pip install --upgrade pip && pip install --no-cache-dir -r $PIP_REQUIREMENTS_FILE

COPY . .
