# Telegram bot: Check novel/comic websites update

## Introduction

This bot scans novel websites (e.g. <http://www.wutuxs.com>), and send telegram message upon release of latest chapter.

The checking period is limited to be `once per min` between 6pm and 11pm to reduce traffic.

### Screenshots

```sh
[2020/07/06 10:00:00] Program Start!
[2020/07/06 10:00:00] Check hour range: 18:00:00 - 22:00:00
[2020/07/06 10:00:01] Current chapter:  第一千两百八十八章 三人组
[2020/07/06 18:01:01] No update found
[2020/07/06 18:02:01] No update found
[2020/07/06 18:03:01] No update found
.
.
.
[2020/07/06 20:34:01 No update found
[2020/07/06 20:35:01 No update found
Update found!
```

## How to use

choose either option below to run the application

### Option 1: Python

1. Set your `token` and `chat_id` in `/tg/config.py`
2. Start the application with the following command:

```sh
cd app/
pip install -r requirements.txt
python main.py
```

### Option 2: Docker Compose

1. Set your `token` and `chat_id` in `docker-compose.yml`
2. Start the container with the following command:

```sh
docker-compose up -d
```
