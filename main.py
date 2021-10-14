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


LIST_YAML_PATH = "list.yaml"

tg_helper = TgHelper()


def syosetu_checker(syosetu_helper, show_no_update_msg=False):
    novel_name = syosetu_helper.name
    if syosetu_helper.check_update():
        print_t(
            f"Update found for {syosetu_helper.name}:"
            f" {syosetu_helper.latest_chapter_title} ({syosetu_helper.translate_url})"
        )

        content = f"novel <<{novel_name}>> updated!"
        url_text = f"<<{novel_name}>> {syosetu_helper.latest_chapter_title}"
        tg_helper.send_channel(
            content=content,
            url_text=url_text,
            url=syosetu_helper.translate_url,
        )
    else:
        if show_no_update_msg:
            print_t(f"No update found for {novel_name}")


def wutuxs_checker(wutuxs_helper, show_no_update_msg=False):
    novel_name = wutuxs_helper.name
    if wutuxs_helper.check_update():
        print_t(
            f"Update found for {wutuxs_helper.name}:"
            f" {wutuxs_helper.latest_chapter_title} ({wutuxs_helper.latest_chapter_url})"
        )

        content = f"novel <<{novel_name}>> updated!"
        url_text = f"<<{novel_name}>> {wutuxs_helper.latest_chapter_title}"
        tg_helper.send_channel(
            content=content,
            url_text=url_text,
            url=wutuxs_helper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            print_t(f"No update found for {novel_name}")


def qiman6_checker(qiman6_helper, show_no_update_msg=False):
    comic_name = qiman6_helper.name
    if qiman6_helper.check_update():
        print_t(
            f"Update found for {qiman6_helper.name}:"
            f" {qiman6_helper.latest_chapter_title} ({qiman6_helper.latest_chapter_url})"
        )

        content = f"comic <<{comic_name}>> updated!"
        url_text = f"<<{comic_name}>> {qiman6_helper.latest_chapter_title}"
        tg_helper.send_channel(
            content=content,
            url_text=url_text,
            url=qiman6_helper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            print_t(f"No update found for {comic_name}")


# def cocomanhua_checker(cocomanhua_helper, show_no_update_msg=False):
#     comic_name = cocomanhua_helper.name
#     if cocomanhua_helper.check_update():
#         print_t(
#             f"Update found for {cocomanhua_helper.name}:"
#             f" {cocomanhua_helper.latest_chapter_title} ({cocomanhua_helper.latest_chapter_url})"
#         )

#         content = f"comic <<{comic_name}>> updated!"
#         url_text = f"<<{comic_name}>> {cocomanhua_helper.latest_chapter_title}"
#         tg_helper.send_channel(
#             content=content,
#             url_text=url_text,
#             url=cocomanhua_helper.latest_chapter_url,
#         )
#     else:
#         if show_no_update_msg:
#             print_t(f"No update found for {comic_name}")


def manhuagui_checker(manhuagui_helper, show_no_update_msg=False):
    comic_name = manhuagui_helper.name
    if manhuagui_helper.check_update():
        print_t(
            f"Update found for {manhuagui_helper.name}:"
            f" {manhuagui_helper.latest_chapter_title} ({manhuagui_helper.latest_chapter_url})"
        )

        content = f"comic <<{comic_name}>> updated!"
        url_text = f"<<{comic_name}>> {manhuagui_helper.latest_chapter_title}"
        tg_helper.send_channel(
            content=content,
            url_text=url_text,
            url=manhuagui_helper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            print_t(f"No update found for {comic_name}")


def esjzone_checker(esjzone_helper, show_no_update_msg=False):
    novel_name = esjzone_helper.name
    if esjzone_helper.check_update():
        print_t(
            f"Update found for {esjzone_helper.name}:"
            f" {esjzone_helper.latest_chapter_title} ({esjzone_helper.latest_chapter_url})"
        )

        content = f"novel <<{novel_name}>> updated!"
        url_text = f"<<{novel_name}>> {esjzone_helper.latest_chapter_title}"
        tg_helper.send_channel(
            content=content,
            url_text=url_text,
            url=esjzone_helper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            print_t(f"No update found for {novel_name}")


def main():
    """main"""
    # print_t("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    with open(LIST_YAML_PATH, encoding="utf8") as list_file:
        data = yaml.load(list_file, Loader=yaml.FullLoader)

    # cocomanhua_helper_list = []
    wutuxs_helper_list = []
    manhuagui_helper_list = []
    esjzone_helper_list = []
    syosetu_helper_list = []
    qiman6_helper_list = []
    for item in data:
        # if Cocomanhua_helper.match(item["url"]):
        #     cocomanhua_helper_list.append(
        #         Cocomanhua_helper(name=item["name"], url=item["url"])
        #     )
        if WutuxsHelper.match(item["url"]):
            wutuxs_helper_list.append(
                WutuxsHelper(name=item["name"], url=item["url"])
            )
        if ManhuaguiHelper.match(item["url"]):
            manhuagui_helper_list.append(
                ManhuaguiHelper(name=item["name"], url=item["url"])
            )
        if EsjzoneHelper.match(item["url"]):
            esjzone_helper_list.append(
                EsjzoneHelper(name=item["name"], url=item["url"])
            )
        if SyosetuHelper.match(item["url"]):
            syosetu_helper_list.append(
                SyosetuHelper(
                    name=item["name"],
                    url=item["url"],
                    translate_url=item["translate_url"],
                )
            )
        if Qiman6Helper.match(item["url"]):
            qiman6_helper_list.append(
                Qiman6Helper(name=item["name"], url=item["url"])
            )

    # for cocomanhua_helper in cocomanhua_helper_list:
    #     print_t(
    #         f"Current chapter for comic {cocomanhua_helper.name}:"
    #         f" {cocomanhua_helper.latest_chapter_title} ({cocomanhua_helper.latest_chapter_url})"
    #     )
    #     schedule.every(5).to(30).minutes.do(
    #         cocomanhua_checker,
    #         cocomanhua_helper=cocomanhua_helper,
    #         show_no_update_msg=False,
    #     )
    for wutuxs_helper in wutuxs_helper_list:
        print_t(
            f"Current chapter for novel {wutuxs_helper.name}:"
            f" {wutuxs_helper.latest_chapter_title} ({wutuxs_helper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            wutuxs_checker,
            wutuxs_helper=wutuxs_helper,
            show_no_update_msg=False,
        )
    for manhuagui_helper in manhuagui_helper_list:
        print_t(
            f"Current chapter for comic {manhuagui_helper.name}:"
            f" {manhuagui_helper.latest_chapter_title} ({manhuagui_helper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            manhuagui_checker,
            manhuagui_helper=manhuagui_helper,
            show_no_update_msg=False,
        )
    for esjzone_helper in esjzone_helper_list:
        print_t(
            f"Current chapter for novel {esjzone_helper.name}:"
            f" {esjzone_helper.latest_chapter_title} ({esjzone_helper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            esjzone_checker,
            esjzone_helper=esjzone_helper,
            show_no_update_msg=False,
        )
    for syosetu_helper in syosetu_helper_list:
        print_t(
            f"Current chapter for novel {syosetu_helper.name}:"
            f" {syosetu_helper.latest_chapter_title} ({syosetu_helper.translate_url})"
        )
        schedule.every(5).to(30).minutes.do(
            syosetu_checker,
            syosetu_helper=syosetu_helper,
            show_no_update_msg=False,
        )
    for qiman6_helper in qiman6_helper_list:
        print_t(
            f"Current chapter for comic {qiman6_helper.name}: "
            f"{qiman6_helper.latest_chapter_title} ({qiman6_helper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            qiman6_checker,
            qiman6_helper=qiman6_helper,
            show_no_update_msg=False,
        )

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    print_t("Program Start!")
    main()
