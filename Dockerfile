FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y git
ENV PYTHON_VERSION=3.11

COPY . .

CMD ["python", "app.py"]