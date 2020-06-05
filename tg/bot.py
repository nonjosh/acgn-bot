import telegram
from tg.config import BotConfig, ChannelConfig

TOKEN = BotConfig.token
chat_id = ChannelConfig.chat_id

def send_channel(content='No input content'):
    bot = telegram.Bot(token=TOKEN)
    bot.sendMessage(chat_id=chat_id,
                    text=content,
                    parse_mode=telegram.ParseMode.HTML)