# Telegram bot: Check novel/comic websites update

## Introduction

This bot scans novel websites (e.g. <http://www.wutuxs.com>), and send telegram message upon release of latest chapter.

The checking period is limited to be `once per min` between 6pm and 11pm to reduce traffic.

## How to use

### Setting environment variables

1. Set your `token` and `chat_id` in `/tg/config.py` or `docker-compose.yml`
2. Start the container with the following command:

### Run the Application

#### Python

```bash
python main.py
```

#### Docker-compose

```sh
docker-compose up -d
```
