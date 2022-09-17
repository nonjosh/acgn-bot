# Telegram bot: Check anime/comic/game/novel websites update

![docker build workflow](https://github.com/nonjosh/acgn-bot/actions/workflows/docker-build.yml/badge.svg)
![pylint workflow](https://github.com/nonjosh/acgn-bot/actions/workflows/pylint.yml/badge.svg)
![unittest workflow](https://github.com/nonjosh/acgn-bot/actions/workflows/python-test.yml/badge.svg)
![CodeQL workflow](https://github.com/nonjosh/acgn-bot/actions/workflows/codeql-analysis.yml/badge.svg)

- [Telegram bot: Check anime/comic/game/novel websites update](#telegram-bot-check-animecomicgamenovel-websites-update)
  - [Introduction](#introduction)
    - [Screenshots](#screenshots)
    - [Supported websites](#supported-websites)
    - [Default Settings](#default-settings)
    - [Supported Telegram Commands](#supported-telegram-commands)
    - [Environment Variables](#environment-variables)
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

### Supported websites

| Name      | Example Url                                                    | Media Type |
|-----------|----------------------------------------------------------------|------------|
| wutuxs    | <http://www.wutuxs.com/html/9/9715/>                           | novel      |
| syosetu   | <https://ncode.syosetu.com/n6621fl>                            | novel      |
| 99wx      | <https://www.99wx.cc/wanxiangzhiwang>                          | novel/comic|
| manhuagui | <https://m.manhuagui.com/comic/30903/>                         | comic      |
| qiman     | <http://qiman57.com/19827/>                                    | comic      |
| baozimh   | <https://www.baozimh.com/comic/fangkainagenuwu-yuewenmanhua_e> | comic      |
| xbiquge   | <https://www.xbiquge.la/55/55945/>                             | comic      |
| dashuhuwai| <https://www.dashuhuwai.com/comic/fangkainagenvwu/>            | comic      |
| mn4u      | <https://mn4u.net/zgm-2149/>                                   | comic      |
| comick    | <https://comick.top/yuujin-chara-wa-taihen-desu-ka-manga-raw>  | comic      |

### Default Settings

| Setting              | Default value   |
|----------------------|-----------------|
| Checking Interval    | **_30~60 min_** |
| Retry Interval       | 5 min           |
| Maximum Retry Number | 5               |

### Supported Telegram Commands

| Command       | Description                    |
|---------------|--------------------------------|
| /list_config  | List all valid config websites |
| /list_latest  | List latest chapters           |

### Environment Variables

| Name               | Default value   | Description                                                         |
|--------------------|-----------------|---------------------------------------------------------------------|
| TOKEN              |                 |Telegram Bot Token                                                   |
| CHAT_ID            |                 |Telegram Chat ID                                                     |
| CONFIG_YML_URL     |                 |Config file url (Optional)                                           |
| CONFIG_YML_FILEPATH|config/list.yaml |Config file path (Optional, only used when CONFIG_YML_URL is not set)|

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

- hack cocomanhua cloudflare DDOS protection
- Support other IM bot other than Telegram (e.g. Signal, Discord)
- Add back time range for checking
