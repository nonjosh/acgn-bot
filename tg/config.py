import os

class BotConfig:
    # botA
    token = os.environ.get("TOKEN", '<your token>')

class ChannelConfig:
    # channelA
    chat_id = "<your chat_id>"