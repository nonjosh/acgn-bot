"""main"""
import threading
import time
from typing import Union
import schedule
import chinese_converter
import helpers
from helpers.tg import TgHelper
from helpers.yml_parser import YmlParser
from helpers.utils import get_logger, get_main_domain_name

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
        show_no_update_msg (bool, optional): print no update msg. Defaults to False.
    """
    # Check if old chapter list is empty
    if len(my_helper.checker.chapter_list) == 0:
        # Initialize checker chapter list
        _ = my_helper.checker.get_updated_chapter_list()
        return
    # Check for update
    updated_chapter_list = my_helper.checker.get_updated_chapter_list()
    if len(updated_chapter_list) > 0:

        for updated_chapter in updated_chapter_list:
            # Print update message
            logger.info(
                "Update found for %s: %s (%s)",
                my_helper.name,
                updated_chapter.title,
                updated_chapter.url,
            )

        content_html_text = get_msg_content(my_helper)
        tg_helper.send_msg(content=content_html_text)
    else:
        if show_no_update_msg:
            logger.info(
                "No update found for %s %s",
                my_helper.media_type,
                my_helper.name,
            )


def get_msg_content(
    my_helper: Union[helpers.NovelChapterHelper, helpers.ComicChapterHelper]
) -> str:
    """Construct html message content from helper and urls

    Args:
        my_helper (Helper): helper object

    Returns:
        str: message content (html)
    """

    content_html_text = f"{my_helper.name} {my_helper.media_type} updated!\n"
    urls_texts = [
        f"<a href='{url}'>{get_main_domain_name(url)}</a>"
        for url in my_helper.urls
    ]
    content_html_text += " | ".join(urls_texts) + "\n"

    updated_chapter_list = my_helper.checker.updated_chapter_list
    content_html_text += f"Updated {len(updated_chapter_list)} chapter(s): "
    chapter_texts = [
        f"<a href='{updated_chapter.url}'>{updated_chapter.title}</a>"
        for updated_chapter in updated_chapter_list
    ]
    content_html_text += ", ".join(chapter_texts)

    return chinese_converter.to_traditional(content_html_text)


def print_latest_chapter(
    my_helper: Union[helpers.NovelChapterHelper, helpers.ComicChapterHelper]
) -> None:
    """Print latest chapter"""
    latest_chapter_obj = my_helper.checker.get_latest_chapter()
    if latest_chapter_obj is not None:
        latest_chapter_title = latest_chapter_obj.title
        latest_chapter_url = latest_chapter_obj.url

        logger.info(
            "Current chapter for %s %s: %s (%s)",
            my_helper.media_type,
            my_helper.name,
            latest_chapter_title,
            latest_chapter_url,
        )
    else:
        logger.info(
            "No chapter found for %s %s",
            my_helper.media_type,
            my_helper.name,
        )


def init_helper(
    my_helper: Union[helpers.NovelChapterHelper, helpers.ComicChapterHelper],
) -> None:
    """Initialize helper

    Args:
        my_helper (Helper): helper object
    """
    # Initialize checker chapter list
    _ = my_helper.checker.get_updated_chapter_list()

    # Print latest chapter
    print_latest_chapter(my_helper)


def run_threaded(job_func: callable) -> None:
    """Run job in thread"""
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def add_schedule(
    my_helper: Union[helpers.NovelChapterHelper, helpers.ComicChapterHelper],
    tg_helper: TgHelper,
) -> None:
    """Add task to schedule

    Args:
        my_helper (Helper): [description]
        urls (List[str], optional): [description]. Defaults to None.
    """
    # Initialize helper
    # Define lambda function for init helper
    def init_helper_func():
        return init_helper(my_helper)

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

    # Add schedule for each item
    for item_obj in yml_data:
        # Create helper object and add add to schedule
        if "novel_urls" in item_obj:
            novel_helper = helpers.NovelChapterHelper(
                name=item_obj["name"], urls=item_obj["novel_urls"]
            )
            add_schedule(my_helper=novel_helper, tg_helper=tg_helper)
        if "comic_urls" in item_obj:
            comic_helper = helpers.ComicChapterHelper(
                name=item_obj["name"], urls=item_obj["comic_urls"]
            )
            add_schedule(my_helper=comic_helper, tg_helper=tg_helper)

    # Print how many tasks added
    if len(schedule.jobs) > 0:
        logger.info(
            "Scheduled %s checker(s) successfully.", len(schedule.jobs)
        )
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
