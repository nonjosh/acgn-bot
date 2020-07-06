import os

class BotConfig:
    # bot
    token = os.environ.get('TOKEN', '<your token>')

class ChannelConfig:
    # channel
    chat_id = os.environ.get('CHAT_ID', '<your chat_id>')