FROM python:3.8-slim-buster

ENV TZ=Asia/Hong_Kong

COPY app/requirements.txt /app/

RUN pip install -r /app/requirements.txt

COPY app /app
WORKDIR /app

CMD ["python", "-u", "main.py"]