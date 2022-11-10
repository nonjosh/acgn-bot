"""Telegram Helper"""
import os
import time
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler
from telegram.ext.callbackcontext import CallbackContext
from dotenv import load_dotenv
from helpers.utils import get_logger
from helpers.message import MessageHelper

load_dotenv()
TOKEN = os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

logger = get_logger(__name__)


class TgHelper:
    """Telegram helper"""

    def __init__(self, token: str = TOKEN, chat_id: str = CHAT_ID) -> None:

        if token is None:
            raise ValueError("Telegram bot token is not given")
        if chat_id is None:
            raise ValueError("Chat id is not given")

        self.token = token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=self.token)

        # Create the Updater and pass it your bot's token.
        # Make sure to set use_context=True to use the new context based callbacks
        # Post version 12 this will no longer be necessary
        self.updater = Updater(self.token, use_context=True)

        # Get the dispatcher to register handlers
        self.dispatcher = self.updater.dispatcher

        # on different commands - answer in Telegram
        self.dispatcher.add_handler(
            CommandHandler("list_config", self.list_config)
        )
        self.dispatcher.add_handler(
            CommandHandler("list_latest", self.list_latest)
        )
        self.dispatcher.add_handler(
            CommandHandler("list_last_check", self.list_last_check)
        )

        # log all errors
        self.dispatcher.add_error_handler(self.error)

    def run(self) -> None:
        """Start the bot."""
        # Start the Bot
        self.updater.start_polling()

    def send_msg(
        self,
        content="No input content",
        url_text: str = None,
        url: str = None,
        html: bool = True,
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
                logger.error("Error occurs for %s: %s", content, err)
                logger.error("Waiting %i secs and re-trying...", wait)
                time.sleep(wait * 1000)
                retries += 1

    def list_config(self, update: Update, _: CallbackContext) -> None:
        """Send a message when the command /list_config is issued."""

        html_response = MessageHelper().get_config_list_html_message()
        update.message.reply_html(html_response, disable_web_page_preview=True)

    def list_latest(self, update: Update, _: CallbackContext) -> None:
        """Send a message when the command /list_latest is issued."""
        html_response = MessageHelper().get_latest_chapter_list_html_message()
        update.message.reply_html(html_response, disable_web_page_preview=True)

    def list_last_check(self, update: Update, _: CallbackContext) -> None:
        """List last check time of each helper when the command /list_last_check is issued."""
        html_response = MessageHelper().get_last_check_time_list_html_message()
        update.message.reply_html(html_response, disable_web_page_preview=True)

    def error(self, update: Update, context: CallbackContext) -> None:
        """Log Errors caused by Updates."""
        # Skip for telegram server throttling
        if isinstance(
            context.error.__context__,
            telegram.vendor.ptb_urllib3.urllib3.exceptions.MaxRetryError,
        ):
            return

        logger.warning('Update "%s" caused error "%s"', update, context.error)
