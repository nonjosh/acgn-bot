"""Telegram Helper"""
import os
import time
import telegram
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")


class TgHelper:
    """Telegram helper"""

    def __init__(self, token=TOKEN, chat_id=CHAT_ID) -> None:
        self.token = token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=self.token)

    def send_msg(
        self, content="No input content", url_text=None, url=None, html=True
    ) -> None:
        """Send message to channel

        Args:
            content (str, optional): message content. Defaults to "No input content".
            url_text (str, optional): url text. Defaults to None.
            url (str, optional): url. Defaults to None.
            html (bool, optional): is html. Defaults to True.
        """

        # Set parse_mode to HTML if html is True
        parse_mode = telegram.ParseMode.HTML if html else None

        # Construct reply button if url_text and url are given
        reply_markup = None
        if url is not None:
            url_button = telegram.InlineKeyboardButton(
                text=url_text,  # text that show to user
                url=url,  # text that send to bot when user tap button
            )
            reply_markup = telegram.InlineKeyboardMarkup([[url_button]])

        # Send message
        retries = 1
        success = False
        while not success:
            try:
                self.bot.send_message(
                    chat_id=self.chat_id,
                    text=content,
                    parse_mode=parse_mode,
                    reply_markup=reply_markup,
                )
                success = True
            except telegram.TelegramError as err:
                wait = retries * 30
                print(f"Error occurs for {content}: {err}")
                print(f"Waiting {wait} secs and re-trying...")
                time.sleep(wait * 1000)
                retries += 1
