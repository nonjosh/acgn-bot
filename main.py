import time
import schedule
import yaml
from helpers import (
    print_t,
    TgHelper,
    # CocomanhuaHelper,
    WutuxsHelper,
    ManhuaguiHelper,
    EsjzoneHelper,
    SyosetuHelper,
    Qiman6Helper,
)


LIST_YAML_PATH = "config/list.yaml"

tg_helper = TgHelper()


def my_checker(my_helper, show_no_update_msg=False):
    name = my_helper.name
    if my_helper.check_update():
        if hasattr(my_helper, "translate_url"):
            url = my_helper.translate_url
        else:
            url = my_helper.latest_chapter_url
        print_t(
            f"Update found for {my_helper.name}:"
            f" {my_helper.latest_chapter_title} ({url})"
        )

        content = f"{my_helper.media_type} <<{name}>> updated!"
        url_text = f"<<{name}>> {my_helper.latest_chapter_title}"
        tg_helper.send_channel(
            content=content,
            url_text=url_text,
            url=url,
        )
    else:
        if show_no_update_msg:
            print_t(f"No update found for {my_helper.media_type} {name}")


def main():
    """main"""
    # print_t("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    with open(LIST_YAML_PATH, encoding="utf8") as list_file:
        data = yaml.load(list_file, Loader=yaml.FullLoader)

    helper_list = [
        # CocomanhuaHelper,
        WutuxsHelper,
        ManhuaguiHelper,
        EsjzoneHelper,
        SyosetuHelper,
        Qiman6Helper,
    ]
    for item in data:
        for helper in helper_list:
            if helper.match(item["url"]):
                my_helper = helper(name=item["name"], url=item["url"])
                print_t(
                    "Current chapter for"
                    f" {my_helper.media_type} {my_helper.name}:"
                    f" {my_helper.latest_chapter_title} ({my_helper.latest_chapter_url})"
                )
                schedule.every(5).to(30).minutes.do(
                    my_checker,
                    my_helper,
                    show_no_update_msg=False,
                )
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    print_t("Program Start!")
    main()
