FROM python:3.7.7

COPY . /app

RUN pip install -r /app/requirements.txt

CMD ["python", "-u", "/app/main.py"]