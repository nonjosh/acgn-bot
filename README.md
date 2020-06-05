# Telegram bot: Check novel update

## Introduction

This bot scans novel websites (e.g. http://www.wutuxs.com), and send telegram message upon release of latest chapter.

The checking period is limited to be `once per min` between 6pm and 11pm to reduce traffic.

## How to use

1. Set your `token` and `chat_id` in `/tg/config.py`
2. Start the container with the following command:

```sh
docker-compose up -d
```