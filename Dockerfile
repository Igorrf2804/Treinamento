FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update \
    && apt-get install -y git \
    && apt-get install -y python3-dev libpq-dev build-essential \
    && pip install -r requirements.txt
ENV PYTHON_VERSION=3.11

COPY . .

CMD ["python", "app.py"]