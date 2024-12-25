FROM python:3.14.0a3-slim-bullseye

ENV TZ=Asia/Hong_Kong

COPY requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "-u", "main.py"]
