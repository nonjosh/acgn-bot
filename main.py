"""main"""
import time
import schedule
import helpers
from utils import get_logger

LIST_YAML_PATH = "config/list.yaml"

logger = get_logger(__name__)
tg_helper = helpers.tg.TgHelper()


def job(my_helper, show_no_update_msg=False):
    """job for schedule

    Args:
        my_helper (Helper): helper
        show_no_update_msg (bool, optional): print no update msg. Defaults to False.
    """
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


def get_msg_content(my_helper) -> str:
    """Construct html message content from helper and urls

    Args:
        my_helper (Helper): helper object

    Returns:
        str: message content (html)
    """

    content_html_text = f"{my_helper.name} {my_helper.media_type} updated!\n"
    urls_texts = [
        f"<a href='{url}'>{my_helper.main_domain_name}</a>"
        for url in my_helper.urls
    ]
    content_html_text += " | ".join(urls_texts) + "\n"

    content_html_text += "Updated chapter(s):"
    updated_chapter_list = my_helper.checker.updated_chapter_list
    chapter_texts = [
        f"<a href='{updated_chapter.url}'>{updated_chapter.title}</a>"
        for updated_chapter in updated_chapter_list
    ]
    content_html_text += ", ".join(chapter_texts)

    return content_html_text


def print_latest_chapter(my_helper) -> None:
    """Print latest chapter"""
    latest_chapter_obj = my_helper.checker.get_latest_chapter()
    latest_chapter_title = latest_chapter_obj.title
    latest_chapter_url = latest_chapter_obj.url

    logger.info(
        "Current chapter for %s %s: %s (%s)",
        my_helper.media_type,
        my_helper.name,
        latest_chapter_title,
        latest_chapter_url,
    )


def add_schedule(my_helper) -> None:
    """Add task to schedule

    Args:
        my_helper (Helper): [description]
        urls (List[str], optional): [description]. Defaults to None.
    """
    # Initialize checker chapter list
    _ = my_helper.checker.get_updated_chapter_list()

    # Print latest chapter
    print_latest_chapter(my_helper)

    # Add schedule
    schedule.every(30).to(60).minutes.do(
        job,
        my_helper=my_helper,
        show_no_update_msg=False,
    )


def main():
    """Main logic"""
    # logger.info("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    yml_data = helpers.ymlParser.YmlParser(
        yml_filepath=LIST_YAML_PATH
    ).yml_data

    # Add schedule for each item
    for item_obj in yml_data:
        # Create helper object and add add to schedule
        if "novel_urls" in item_obj:
            novel_helper = helpers.NovelChapterHelper(
                name=item_obj["name"], urls=item_obj["novel_urls"]
            )
            add_schedule(novel_helper)
        if "comic_urls" in item_obj:
            comic_helper = helpers.ComicChapterHelper(
                name=item_obj["name"], urls=item_obj["comic_urls"]
            )
            add_schedule(comic_helper)

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
