FROM python:3.6.1

ENV PYTHONUNBUFFERED 1

COPY . /app
WORKDIR /app
RUN pip install --process-dependency-links -e .
