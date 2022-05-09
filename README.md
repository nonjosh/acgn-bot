# Telegram bot: Check anime/comic/game/novel websites update

![docker build workflow](https://github.com/nonjosh/acgn-bot/actions/workflows/docker-build.yml/badge.svg)
![pylint workflow](https://github.com/nonjosh/acgn-bot/actions/workflows/pylint.yml/badge.svg)

- [Telegram bot: Check anime/comic/game/novel websites update](#telegram-bot-check-animecomicgamenovel-websites-update)
  - [Introduction](#introduction)
    - [Screenshots](#screenshots)
    - [Default Settings](#default-settings)
  - [How to use](#how-to-use)
    - [Setup](#setup)
      - [Option 1: Python](#option-1-python)
      - [Option 2: Docker Compose](#option-2-docker-compose)
      - [Option 3: Kubernetes](#option-3-kubernetes)
    - [Edit your list](#edit-your-list)
  - [Features to add](#features-to-add)

## Introduction

This bot scans anime/comic/game/novel websites, and send telegram message to specific channel/group/chat upon new chapters releases.

### Screenshots

![alt text](img/terminal-output.png)
![alt text](img/tg-output.png)

### Default Settings

Checking interval: **_30~60 min_**

RETRY_INTERVAL: 5min

MAX_RETRY_NUM: 5

Current supported websites:

- novel:
  - <http://www.wutuxs.com>
  - <https://www.esjzone.cc> (Only works for in-site links)
  - <https://ncode.syosetu.com>
- comic:
  - ~~<https://www.cocomanhua.com>~~ (no long support due to Cloudflare Protection)
  - <https://m.manhuagui.com>
  - <http://qiman6.com>
  - <https://www.baozimh.com>

## How to use

### Setup

Choose either option below to run the application

#### Option 1: Python

1. Create `.env`

    ```sh
    TOKEN=<your token>
    CHAT_ID=<your chat_id>
    ```

2. Start the application with the following command:

    ```sh
    pip install -r requirements.txt
    python main.py
    ```

#### Option 2: Docker Compose

1. Create `.env`

    ```sh
    TOKEN=<your token>
    CHAT_ID=<your chat_id>
    ```

2. Start the container with the following command:

    ```sh
    docker-compose up -d
    ```

#### Option 3: Kubernetes

1. Set your bot token and chat_id in `secret/acgn-bot`

    ```sh
    # Examples in k8s/secrets/k8s-secrets.yaml, remember to change to your token/chat_id first
    kubectl apply -f k8s/secrets/k8s-secrets.yaml
    ```

2. Set your checking list yaml file in `configmap/acgn-bot.list.yaml`

    ```sh
    kubectl create configmap acgn-bot.list.yaml --from-file=config/list.yaml --dry-run=client -o yaml | kubectl apply -f -
    ```

3. Build local image and create deployment

    ```sh
    docker build . -t nonjosh/acgn-bot
    kubectl apply -k k8s/base
    ```

### Edit your list

Edit your list in the file `list.yaml`. Restart container to apply changes.

## Features to add

- [ ] Support update notification of multiple chapters
- [ ] Add pytest
- [ ] Show error for invalid pages (e.g. esjzone)
- [ ] hack cocomanhua cloudflare DDOS protection
- [ ] add support for mangatoro.com
- [ ] Support other IM bot other than Telegram (e.g. Signal, Discord)
- [ ] Add back time range for checking
