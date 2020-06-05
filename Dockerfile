FROM python:3.8-slim-buster

ENV TZ=Asia/Hong_Kong

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY . /app
WORKDIR /app

CMD ["python", "-u", "main.py"]