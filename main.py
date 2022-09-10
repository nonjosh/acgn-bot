"""main"""
import threading
import time
from typing import Union
import schedule
import helpers
from helpers.tg import TgHelper
from helpers.yml_parser import YmlParser
from helpers.utils import get_logger

DEFAULT_LIST_YAML_PATH = "config/list.yaml"

logger = get_logger(__name__)


def job(
    my_helper: Union[helpers.NovelChapterHelper, helpers.ComicChapterHelper],
    tg_helper: TgHelper,
    show_no_update_msg=False,
) -> None:
    """job for schedule

    Args:
        my_helper (Helper): helper
        tg_helper (TgHelper): tg helper
        show_no_update_msg (bool, optional): print no update msg. Defaults to False.
    """
    # Initialize checker chapter list if list is empty originally
    if len(my_helper.checker.chapter_list) == 0:
        # Initialize checker chapter list
        updated_chapter_list = my_helper.checker.get_updated_chapter_list()

        # Print latest chapter if success
        if len(updated_chapter_list) > 0:
            latest_chapter_obj = updated_chapter_list[-1]
            latest_chapter_title = latest_chapter_obj.title
            latest_chapter_url = latest_chapter_obj.url
            logger.info(
                "%d chapters found for %s %s - latest: %s (%s)",
                len(updated_chapter_list),
                my_helper.media_type,
                my_helper.name,
                latest_chapter_title,
                latest_chapter_url,
            )
        else:
            if show_no_update_msg:
                logger.info(
                    "Cannot get chapter list for %s %s",
                    my_helper.media_type,
                    my_helper.name,
                )
        return

    # Check for update
    updated_chapter_list = my_helper.checker.get_updated_chapter_list()
    if len(updated_chapter_list) > 0:

        # Print update message for each chapter in terminal
        for updated_chapter in updated_chapter_list:
            logger.info(
                "Update found for %s: %s (%s)",
                my_helper.name,
                updated_chapter.title,
                updated_chapter.url,
            )

        # Send update message to telegram
        content_html_text = my_helper.get_msg_content()
        tg_helper.send_msg(content=content_html_text)
    else:
        # Print no update message for each chapter in terminal (if enabled)
        if show_no_update_msg:
            logger.info(
                "No update found for %s %s",
                my_helper.media_type,
                my_helper.name,
            )


def run_threaded(job_func: callable) -> None:
    """Run job in thread
    Args:
        job_func (callable): job function
    """
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def add_schedule(
    my_helper: Union[helpers.NovelChapterHelper, helpers.ComicChapterHelper],
    tg_helper: TgHelper,
) -> None:
    """Add task to schedule

    Args:
        my_helper (Helper): [description]
        tg_helper (TgHelper): [description]
        urls (List[str], optional): [description]. Defaults to None.
    """
    # Initialize helper
    # Define lambda function for init helper
    def init_helper_func():
        return job(my_helper, tg_helper)

    run_threaded(job_func=init_helper_func)

    # Add schedule thread
    # Define lambda function for job
    def job_func():
        return job(my_helper, tg_helper)

    schedule.every(30).to(60).minutes.do(run_threaded, job_func)


def main():
    """Main logic"""
    tg_helper = TgHelper()

    yml_data = YmlParser(yml_filepath=DEFAULT_LIST_YAML_PATH).yml_data

    my_helper_list = []
    # Add schedule for each item
    for item_obj in yml_data:
        # Create helper object and add add to schedule
        if "novel_urls" in item_obj:
            novel_helper = helpers.NovelChapterHelper(
                name=item_obj["name"], urls=item_obj["novel_urls"]
            )
            my_helper_list.append(novel_helper)

        if "comic_urls" in item_obj:
            comic_helper = helpers.ComicChapterHelper(
                name=item_obj["name"], urls=item_obj["comic_urls"]
            )
            my_helper_list.append(comic_helper)

    # Print how many tasks added
    if len(schedule.jobs) > 0:
        logger.info("Scheduling %s checker(s) ....", len(schedule.jobs))
        for my_helper in my_helper_list:
            add_schedule(my_helper, tg_helper)
    else:
        raise ValueError(
            "No schedule job found, please check format in list.yaml"
        )

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    logger.info("Program Start!")
    main()
