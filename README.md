# Telegram bot: Check novel/comic websites update

## Introduction

This bot scans novel websites (e.g. <http://www.wutuxs.com>), and send telegram message upon release of latest chapter.

The checking period is limited to be `once per min` between 6pm and 11pm to reduce traffic.

### Screenshots

```sh
10:00:00 Program Start!
Check hour range: 18:00:00 - 22:00:00
10:00:01 Current chapter:  第一千两百八十八章 三人组
18:01:01 No update found
18:02:01 No update found
18:03:01 No update found
.
.
.
20:34:01 No update found
20:35:01 No update found
Update found!
```

## How to use

### Setting environment variables

1. Set your `token` and `chat_id` in `/tg/config.py` or `docker-compose.yml`
2. Start the container with the following command:

### Run the Application

choose either option below to run the application

#### Option 1: Python

```bash
python main.py
```

#### Option 2: Docker-compose

```sh
docker-compose up -d
```
