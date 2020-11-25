# Telegram bot: Check novel/comic websites update

## Introduction

This bot scans novel websites (e.g. <http://www.wutuxs.com>), and send telegram message upon release of latest chapter.

The checking period is limited to be `once per min` between 6pm and 11pm to reduce traffic.

### Screenshots

```sh
[2020/11/23 01:43:01] Program Start!
[2020/11/23 01:43:01] Check hour range: 18:00:00 - 22:00:00
[2020/11/23 01:43:02] Current chapter: 第一千四百二十八章 周元入圣
[2020/11/23 20:38:02] Update found! 第一千四百二十九章 混元归位
...
```

## How to use

choose either option below to run the application

### Option 1: Python

1. Set your `token` and `chat_id` in `/tg/config.py`
2. Start the application with the following command:

    ```sh
    pip install -r requirements.txt
    python main.py
    ```

### Option 2: Docker Compose

1. Set your `token` and `chat_id` in `docker-compose.yml`
2. Start the container with the following command:

    ```sh
    docker-compose up -d
    ```

### Option 3: Kubernetes

1. Create your `secret/acgn-bot`

    ```sh
    # Examples in k8s/secrets/k8s-secrets.yaml, remember to change to your token/chat_id first
    kubectl apply -f k8s/secrets/k8s-secrets.yaml
    ```

2. Build local image and create deployment

    ```sh
    docker build . -t nonjosh/acgn-bot
    kubectl apply -k k8s/base
    ```
