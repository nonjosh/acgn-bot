"""Telegram Helper"""
import os

import telegram
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler

from helpers.message import MessageHelper
from helpers.utils import get_logger

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

        self.application = ApplicationBuilder().token(self.token).build()
        self.bot: Bot = self.application.bot

        # on different commands - answer in Telegram
        self.application.add_handler(CommandHandler("list_config", self.list_config))
        self.application.add_handler(CommandHandler("list_latest", self.list_latest))
        self.application.add_handler(
            CommandHandler("list_last_check", self.list_last_check)
        )

    def run(self) -> None:
        """Start the bot."""
        # Start the Bot
        self.application.run_polling()

    async def send_msg(
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
        parse_mode = telegram.constants.ParseMode.HTML if html else None

        # Construct reply button if url_text and url are given
        reply_markup = None
        if url is not None:
            url_button = telegram.InlineKeyboardButton(
                text=url_text,  # text that show to user
                url=url,  # text that send to bot when user tap button
            )
            reply_markup = telegram.InlineKeyboardMarkup([[url_button]])

        # Send message
        bot = telegram.Bot(token=self.token)
        await bot.send_message(
            chat_id=self.chat_id,
            text=content,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
        )

    def send_msg_sync(
        self,
        content="No input content",
        url_text: str = None,
        url: str = None,
        html: bool = True,
    ) -> None:
        """Send message to channel synchronously (thread-safe)

        Args:
            content (str, optional): message content. Defaults to "No input content".
            url_text (str, optional): url text. Defaults to None.
            url (str, optional): url. Defaults to None.
            html (bool, optional): is html. Defaults to True.
        """
        import asyncio
        import threading
        
        # Set parse_mode to HTML if html is True
        parse_mode = telegram.constants.ParseMode.HTML if html else None

        # Construct reply button if url_text and url are given
        reply_markup = None
        if url is not None:
            url_button = telegram.InlineKeyboardButton(
                text=url_text,  # text that show to user
                url=url,  # text that send to bot when user tap button
            )
            reply_markup = telegram.InlineKeyboardMarkup([[url_button]])

        async def _send_message():
            # Send message
            bot = telegram.Bot(token=self.token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=content,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
            )

        # Try to run the coroutine in the current thread's event loop
        try:
            # Check if we're in the main thread and there's a running event loop
            current_loop = None
            try:
                current_loop = asyncio.get_running_loop()
            except RuntimeError:
                pass
            
            if current_loop and not current_loop.is_closed():
                # We have a running event loop, use run_coroutine_threadsafe
                if threading.current_thread() != threading.main_thread():
                    # We're in a different thread, use run_coroutine_threadsafe
                    future = asyncio.run_coroutine_threadsafe(_send_message(), current_loop)
                    future.result()  # Wait for completion
                else:
                    # We're in the main thread with a running loop, can't use run_until_complete
                    # This shouldn't happen in our use case, but handle it gracefully
                    raise RuntimeError(
                        "Cannot run sync method from main thread with a running event loop. "
                        "Consider running this method in a separate thread or ensuring the event loop "
                        "is properly managed to avoid conflicts."
                    )
            else:
                # No running event loop, create a new one
                # Use asyncio.run which properly handles loop lifecycle
                asyncio.run(_send_message())
                
        except Exception as e:
            # If all else fails, try the robust fallback approach
            from helpers.utils import get_logger
            logger = get_logger(__name__)
            logger.error("Primary async approach failed: %s", e)
            try:
                # Create a new event loop in a more robust way
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(_send_message())
                finally:
                    try:
                        # Clean shutdown of the loop
                        pending = asyncio.all_tasks(loop)
                        for task in pending:
                            task.cancel()
                        if pending:
                            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                    except Exception:
                        pass  # Ignore cleanup errors
                    finally:
                        loop.close()
            except Exception as fallback_error:
                from helpers.utils import get_logger
                logger = get_logger(__name__)
                logger.error("Fallback async approach also failed: %s", fallback_error)
                raise

    async def list_config(self, update: Update, _: CallbackContext) -> None:
        """Send a message when the command /list_config is issued."""

        logger.info("The /list_config command is issued")
        html_response = MessageHelper().get_config_list_html_message()
        await update.message.reply_html(html_response, disable_web_page_preview=True)

    async def list_latest(self, update: Update, _: CallbackContext) -> None:
        """Send a message when the command /list_latest is issued."""
        logger.info("The /list_latest command is issued")
        html_response = MessageHelper().get_latest_chapter_list_html_message()
        await update.message.reply_html(html_response, disable_web_page_preview=True)

    async def list_last_check(self, update: Update, _: CallbackContext) -> None:
        """List last check time of each helper when the command /list_last_check is issued."""
        logger.info("The /list_last_check command is issued")
        html_response = MessageHelper().get_last_check_time_list_html_message()
        await update.message.reply_html(html_response, disable_web_page_preview=True)
