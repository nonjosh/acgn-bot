"""main"""
import time
from typing import List
import yaml
import schedule
from helpers import (
    TgHelper,
    # CocomanhuaHelper,
    WutuxsHelper,
    ManhuaguiHelper,
    EsjzoneHelper,
    SyosetuHelper,
    Qiman6Helper,
    BaozimhHelper,
)
from utils import get_logger, get_main_domain_name

LIST_YAML_PATH = "config/list.yaml"

logger = get_logger(__name__)
tg_helper = TgHelper()


def my_checker(my_helper, urls: List[str], show_no_update_msg=False):
    """my_checker

    Args:
        my_helper (Helper): helper
        show_no_update_msg (bool, optional): print no update msg. Defaults to False.
    """
    has_update = my_helper.check_update()
    if has_update:
        if hasattr(my_helper, "translate_url"):
            url = my_helper.translate_url
        else:
            url = my_helper.latest_chapter_url

        # Print update message
        logger.info(
            "Update found for %s: %s (%s)",
            my_helper.name,
            my_helper.latest_chapter_title,
            url,
        )

        content_html_text = get_msg_content(my_helper, urls)
        tg_helper.send_msg(content=content_html_text)
    else:
        if show_no_update_msg:
            logger.info(
                "No update found for %s %s",
                my_helper.media_type,
                my_helper.name,
            )


def get_msg_content(my_helper, urls: List[str] = None) -> str:
    """Construct html message content from helper and urls

    Args:
        my_helper (Helper): helper object
        urls (List[str], optional): list of urls. Defaults to None.

    Returns:
        str: message content (html)
    """

    content_html_text = f"{my_helper.name} {my_helper.media_type} updated!\n"
    urls_texts = [
        f"<a href='{url}'>{get_main_domain_name(url)}</a>" for url in urls
    ]
    content_html_text += " | ".join(urls_texts) + "\n"
    content_html_text += (
        f"latest chapter: <a href='{my_helper.latest_chapter_url}'>"
        f"{my_helper.latest_chapter_title}</a>"
    )

    return content_html_text


def print_latest_chapter(my_helper):
    """Print latest chapter"""
    logger.info(
        "Current chapter for %s %s: %s (%s)",
        my_helper.media_type,
        my_helper.name,
        my_helper.latest_chapter_title,
        my_helper.latest_chapter_url,
    )


def add_schedule(helper, urls: List[str] = None):
    """Add task to schedule

    Args:
        helper (Helper): [description]
        urls (List[str], optional): [description]. Defaults to None.
    """
    print_latest_chapter(helper)
    schedule.every(30).to(60).minutes.do(
        my_checker,
        my_helper=helper,
        urls=urls,
        show_no_update_msg=False,
    )


def get_helper(item_obj, urls_type: str = "comic_urls"):
    """Define helper based on item_obj

    Args:
        item_obj (dict): item object contains helper name and urls
        urls_type (str, optional): [description]. Defaults to "comic_urls".

    Returns:
        helper
    """
    # Set helper list for checking (default list: comic)
    helper_list = []
    if urls_type == "comic_urls":
        if "comic_urls" in item_obj:
            helper_list = [
                # CocomanhuaHelper,
                # ManhuaguiHelper,
                Qiman6Helper,
                BaozimhHelper,
            ]
    elif urls_type == "novel_urls":
        if "novel_urls" in item_obj:
            helper_list = [
                WutuxsHelper,
                EsjzoneHelper,
                SyosetuHelper,
            ]
    else:
        raise ValueError(f"Unknown urls_type: {urls_type}")

    # Check helper type and return helper
    if len(helper_list) > 0:
        for helper in helper_list:
            if helper.match(item_obj[urls_type][0]):
                return helper(
                    name=item_obj["name"], url=item_obj[urls_type][0]
                )

    return None


def main():
    """Main logic"""
    # logger.info("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    with open(LIST_YAML_PATH, encoding="utf8") as list_file:
        yml_data = yaml.load(list_file, Loader=yaml.FullLoader)

    # Add schedule for each item
    for item_obj in yml_data:
        # Create helper object and add add to schedule
        for urls_type in ["comic_urls", "novel_urls"]:
            helper = get_helper(item_obj, urls_type)
            if helper:
                add_schedule(helper, urls=item_obj[urls_type])

    if len(schedule.jobs) > 0:
        logger.info("Scheduled %s checker(s).", len(schedule.jobs))
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
