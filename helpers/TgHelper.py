import os
import time
import telegram
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("TOKEN")
chat_id = os.environ.get("CHAT_ID")


class TgHelper:
    def __init__(self, token=token, chat_id=chat_id) -> None:
        self.token = token
        self.chat_id = chat_id

    def send_channel(
        self, content="No input content", url_text=None, url=None, html=False
    ):
        bot = telegram.Bot(token=self.token)

        parse_mode = telegram.ParseMode.HTML if html else None

        reply_markup = None
        if url is not None:
            url_button = telegram.InlineKeyboardButton(
                text=url_text,  # text that show to user
                url=url,  # text that send to bot when user tap button
            )
            reply_markup = telegram.InlineKeyboardMarkup([[url_button]])

        retries = 1
        success = False
        while not success:
            try:
                bot.sendMessage(
                    chat_id=self.chat_id,
                    text=content,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                )
                success = True
            except Exception as e:
                wait = retries * 30
                print(f"Error occurs for {content}: {e}")
                print(f"Waiting {wait} secs and re-trying...")
                time.sleep(wait * 1000)
                retries += 1


if __name__ == "__main__":
    tgHelper = TgHelper()
    tgHelper.send_channel(content="Test")
