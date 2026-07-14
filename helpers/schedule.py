"""Schedule helper module."""

import asyncio
import json
import threading
import time

import requests
import schedule
from telegram.error import TelegramError

from helpers.checkers import ManhuaguiChecker
from helpers.media import MEDIA_URL_FIELDS, MediaHelper
from helpers.media_list_state import MediaListState
from helpers.message import MessageHelper
from helpers.tg import TgHelper
from helpers.utils import get_logger

logger = get_logger(__name__)

CHECKER_RUN_EXCEPTIONS = (
    requests.exceptions.RequestException,
    json.decoder.JSONDecodeError,
    ValueError,
    TypeError,
    AttributeError,
    KeyError,
    IndexError,
)

SCHEDULER_JOB_EXCEPTIONS = CHECKER_RUN_EXCEPTIONS + (
    RuntimeError,
    TelegramError,
)


class ScheduleHelper:
    """Schedule helper class"""

    def __init__(self, yml_data: list, tg_helper: TgHelper) -> None:
        """Initialize schedule helper"""

        self.tg_helper = tg_helper

        # Initialize schedule
        schedule.clear()

        # Initialize MediaHelper list
        for item_obj in yml_data:
            # Create helper objects for each supported media url field.
            for url_field, media_type in MEDIA_URL_FIELDS:
                if url_field not in item_obj:
                    continue

                media_helper = MediaHelper(
                    name=item_obj["name"],
                    urls=item_obj[url_field],
                    media_type=media_type,
                )
                MediaListState.media_helper_list.append(media_helper)

        # Add schedules
        if len(MediaListState.media_helper_list) > 0:
            logger.info(
                "Scheduling %s checker(s) ....",
                len(MediaListState.media_helper_list),
            )
            for media_helper in MediaListState.media_helper_list:
                self.add_schedule(media_helper)
            if len(schedule.jobs) > 0:
                logger.info("Scheduled %s checker(s) successfully.", len(schedule.jobs))
            else:
                logger.error("No checker scheduled.")
                raise RuntimeError("No checker scheduled.")

    def add_schedule(
        self,
        media_helper: MediaHelper,
    ) -> None:
        """Add task to schedule

        Args:
            media_helper (MediaHelper): [description]
        """

        def get_updated_chapter_list_safe(media_helper: MediaHelper) -> list:
            """Run checker safely and return updated chapters.

            Any checker exception (e.g. transient HTTP errors / 404) is logged and
            treated as no-update so the scheduler thread keeps running.
            """

            try:
                return media_helper.checker.get_updated_chapter_list()
            except CHECKER_RUN_EXCEPTIONS as err:
                logger.exception(
                    "Checker failed for %s %s (%s): %s",
                    media_helper.media_type,
                    media_helper.name,
                    getattr(media_helper, "check_url", media_helper.urls),
                    err,
                )
                return []

        def job(
            media_helper: MediaHelper,
            show_no_update_msg=False,
        ) -> None:
            """job for schedule

            Args:
                media_helper (MediaHelper): helper
                show_no_update_msg (bool, optional): print no update msg. Defaults to False.
            """
            # Initialize checker chapter list if list is empty originally
            if len(media_helper.checker.chapter_list) == 0:
                # Initialize checker chapter list
                updated_chapter_list = get_updated_chapter_list_safe(media_helper)

                # Print latest chapter if success
                if len(updated_chapter_list) > 0:
                    latest_chapter_obj = updated_chapter_list[-1]
                    latest_chapter_title = latest_chapter_obj.title
                    latest_chapter_url = latest_chapter_obj.url
                    logger.info(
                        "%d chapters found for %s %s - latest: %s (%s)",
                        len(updated_chapter_list),
                        media_helper.media_type,
                        media_helper.name,
                        latest_chapter_title,
                        latest_chapter_url,
                    )
                else:
                    if show_no_update_msg:
                        logger.info(
                            "Cannot get chapter list for %s %s",
                            media_helper.media_type,
                            media_helper.name,
                        )
                return

            # Check for update
            updated_chapter_list = get_updated_chapter_list_safe(media_helper)
            if len(updated_chapter_list) > 0:
                # Print update message for each chapter in terminal
                for updated_chapter in updated_chapter_list:
                    logger.info(
                        "Update found for %s %s: %s (%s)",
                        media_helper.media_type,
                        media_helper.name,
                        updated_chapter.title,
                        updated_chapter.url,
                    )

                # Send update message to telegram
                content_html_text = MessageHelper().get_update_chapters_html_message(
                    media_helper=media_helper,
                )

                async def send_with_retry():
                    retries = 1
                    while retries <= 3:
                        try:
                            await self.tg_helper.send_msg(content=content_html_text)
                            return
                        except TelegramError as err:
                            wait = retries * 30
                            logger.error(
                                "Error occurs for %s %s updated!",
                                media_helper.media_type,
                                media_helper.name,
                            )
                            logger.error(err)
                            logger.error(
                                "Waiting %i secs and re-trying... (%i/%i)",
                                wait,
                                retries,
                                3,
                            )
                            await asyncio.sleep(wait)
                            retries += 1
                    logger.error(
                        "Failed to send message for %s %s after %i retries",
                        media_helper.media_type,
                        media_helper.name,
                        3,
                    )

                loop = None
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(send_with_retry())
                except RuntimeError as err:
                    logger.error("Error occurs: %s", err)
                finally:
                    if loop is not None:
                        loop.close()
            else:
                # Print no update message for each chapter in terminal (if enabled)
                if show_no_update_msg:
                    logger.info(
                        "No update found for %s %s",
                        media_helper.media_type,
                        media_helper.name,
                    )

        # Define lambda function for job
        def job_func() -> None:
            try:
                job(media_helper)
                return None
            except SCHEDULER_JOB_EXCEPTIONS as err:
                logger.exception(
                    "Unexpected scheduler job error for %s %s (%s): %s",
                    media_helper.media_type,
                    media_helper.name,
                    getattr(media_helper, "check_url", media_helper.urls),
                    err,
                )
                return None

        def run_threaded(job_func: callable) -> None:
            """Run job in thread
            Args:
                job_func (callable): job function
            """
            job_thread = threading.Thread(target=job_func)
            job_thread.start()

        # Only add to schedule if checker is set up successfully
        if media_helper.checker:
            # Run for the first time if not Manhuagui
            # because Manhuagui will block ip addresses with high frequency attampts
            if not isinstance(media_helper.checker, ManhuaguiChecker):
                run_threaded(job_func=job_func)

            schedule.every(30).to(60).minutes.do(run_threaded, job_func)
        else:
            logger.error(
                "Cannot add schedule for %s %s (%s)",
                media_helper.media_type,
                media_helper.name,
                media_helper.urls,
            )

    def run(self) -> None:
        """Run schedule"""
        while True:
            schedule.run_pending()
            time.sleep(1)
