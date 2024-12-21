"""Schedule helper module."""
import asyncio
import threading
import time

import schedule

from helpers.checkers import ManhuaguiChecker
from helpers.media import MediaHelper
from helpers.media_list_state import MediaListState
from helpers.message import MessageHelper
from helpers.tg import TgHelper
from helpers.utils import get_logger

logger = get_logger(__name__)


class ScheduleHelper:
    """Schedule helper class"""

    def __init__(self, yml_data: list, tg_helper: TgHelper) -> None:
        """Initialize schedule helper"""

        self.tg_helper = tg_helper

        # Initialize schedule
        schedule.clear()

        # Initialize MediaHelper list
        for item_obj in yml_data:
            # Create helper object and add to list
            if "novel_urls" in item_obj:
                novel_helper = MediaHelper(
                    name=item_obj["name"],
                    urls=item_obj["novel_urls"],
                    media_type="novel",
                )
                MediaListState.media_helper_list.append(novel_helper)

            if "comic_urls" in item_obj:
                comic_helper = MediaHelper(
                    name=item_obj["name"],
                    urls=item_obj["comic_urls"],
                    media_type="comic",
                )
                MediaListState.media_helper_list.append(comic_helper)

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
                raise Exception("No checker scheduled.")

    def add_schedule(
        self,
        media_helper: MediaHelper,
    ) -> None:
        """Add task to schedule

        Args:
            media_helper (MediaHelper): [description]
        """

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
                updated_chapter_list = media_helper.checker.get_updated_chapter_list()

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
            updated_chapter_list = media_helper.checker.get_updated_chapter_list()
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
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(
                        self.tg_helper.send_msg(content=content_html_text)
                    )
                except Exception as err:
                    logger.error("Error occurs: %s", err)
                finally:
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
            return job(media_helper)

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
