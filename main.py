import os
import time
import schedule
import yaml
from helpers import (
    printT,
    TgHelper,
    CocomanhuaHelper,
    WutuxsHelper,
    ManhuaguiHelper,
    EsjzoneHelper,
    SyosetuHelper,
)

LIST_YAML_PATH = "list.yaml"

tgHelper = TgHelper()


def syosetuChecker(syosetuHelper, show_no_update_msg=False):
    novel_name = syosetuHelper.name
    if syosetuHelper.checkUpdate():
        printT(
            f"Update found for {syosetuHelper.name}: {syosetuHelper.latest_chapter_title} ({syosetuHelper.translateUrl})"
        )

        content = f"novel <<{novel_name}>> updated!"
        url_text = f"<<{novel_name}>> {syosetuHelper.latest_chapter_title}"
        tgHelper.send_channel(
            content=content,
            url_text=url_text,
            url=syosetuHelper.translateUrl,
        )
    else:
        if show_no_update_msg:
            printT(f"No update found for {novel_name}")


def wutuxsChecker(wutuxsHelper, show_no_update_msg=False):
    novel_name = wutuxsHelper.name
    if wutuxsHelper.checkUpdate():
        printT(
            f"Update found for {wutuxsHelper.name}: {wutuxsHelper.latest_chapter_title} ({wutuxsHelper.latest_chapter_url})"
        )

        content = f"comic <<{novel_name}>> updated!"
        url_text = f"<<{novel_name}>> {wutuxsHelper.latest_chapter_title}"
        tgHelper.send_channel(
            content=content,
            url_text=url_text,
            url=wutuxsHelper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            printT(f"No update found for {novel_name}")


def cocomanhuaChecker(cocomanhuaHelper, show_no_update_msg=False):
    comic_name = cocomanhuaHelper.name
    if cocomanhuaHelper.checkUpdate():
        printT(
            f"Update found for {cocomanhuaHelper.name}: {cocomanhuaHelper.latest_chapter_title} ({cocomanhuaHelper.latest_chapter_url})"
        )

        content = f"comic <<{comic_name}>> updated!"
        url_text = f"<<{comic_name}>> {cocomanhuaHelper.latest_chapter_title}"
        tgHelper.send_channel(
            content=content,
            url_text=url_text,
            url=cocomanhuaHelper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            printT(f"No update found for {comic_name}")


def manhuaguiChecker(manhuaguiHelper, show_no_update_msg=False):
    comic_name = manhuaguiHelper.name
    if manhuaguiHelper.checkUpdate():
        printT(
            f"Update found for {manhuaguiHelper.name}: {manhuaguiHelper.latest_chapter_title} ({manhuaguiHelper.latest_chapter_url})"
        )

        content = f"comic <<{comic_name}>> updated!"
        url_text = f"<<{comic_name}>> {manhuaguiHelper.latest_chapter_title}"
        tgHelper.send_channel(
            content=content,
            url_text=url_text,
            url=manhuaguiHelper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            printT(f"No update found for {comic_name}")


def esjzoneChecker(esjzoneHelper, show_no_update_msg=False):
    novel_name = esjzoneHelper.name
    if esjzoneHelper.checkUpdate():
        printT(
            f"Update found for {esjzoneHelper.name}: {esjzoneHelper.latest_chapter_title} ({esjzoneHelper.latest_chapter_url})"
        )

        content = f"novel <<{novel_name}>> updated!"
        url_text = f"<<{novel_name}>> {esjzoneHelper.latest_chapter_title}"
        tgHelper.send_channel(
            content=content,
            url_text=url_text,
            url=esjzoneHelper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            printT(f"No update found for {novel_name}")


if __name__ == "__main__":

    printT("Program Start!")

    # printT("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    with open(LIST_YAML_PATH) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    cocomanhuaHelperList = []
    wutuxsHelperList = []
    manhuaguiHelperList = []
    esjzoneHelperList = []
    syosetuHelperList = []
    for item in data:
        if CocomanhuaHelper.match(item["url"]):
            cocomanhuaHelperList.append(
                CocomanhuaHelper(name=item["name"], url=item["url"])
            )
        if WutuxsHelper.match(item["url"]):
            wutuxsHelperList.append(WutuxsHelper(name=item["name"], url=item["url"]))
        if ManhuaguiHelper.match(item["url"]):
            manhuaguiHelperList.append(
                ManhuaguiHelper(name=item["name"], url=item["url"])
            )
        if EsjzoneHelper.match(item["url"]):
            esjzoneHelperList.append(EsjzoneHelper(name=item["name"], url=item["url"]))
        if SyosetuHelper.match(item["url"]):
            syosetuHelperList.append(
                SyosetuHelper(
                    name=item["name"],
                    url=item["url"],
                    translateUrl=item["translateUrl"],
                )
            )

    for cocomanhuaHelper in cocomanhuaHelperList:
        printT(
            f"Current chapter for comic {cocomanhuaHelper.name}: {cocomanhuaHelper.latest_chapter_title} ({cocomanhuaHelper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            cocomanhuaChecker,
            cocomanhuaHelper=cocomanhuaHelper,
            show_no_update_msg=False,
        )
    for wutuxsHelper in wutuxsHelperList:
        printT(
            f"Current chapter for novel {wutuxsHelper.name}: {wutuxsHelper.latest_chapter_title} ({wutuxsHelper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            wutuxsChecker,
            wutuxsHelper=wutuxsHelper,
            show_no_update_msg=False,
        )
    for manhuaguiHelper in manhuaguiHelperList:
        printT(
            f"Current chapter for comic {manhuaguiHelper.name}: {manhuaguiHelper.latest_chapter_title} ({manhuaguiHelper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            manhuaguiChecker,
            manhuaguiHelper=manhuaguiHelper,
            show_no_update_msg=False,
        )
    for esjzoneHelper in esjzoneHelperList:
        printT(
            f"Current chapter for novel {esjzoneHelper.name}: {esjzoneHelper.latest_chapter_title} ({esjzoneHelper.latest_chapter_url})"
        )
        schedule.every(5).to(30).minutes.do(
            esjzoneChecker,
            esjzoneHelper=esjzoneHelper,
            show_no_update_msg=False,
        )
    for syosetuHelper in syosetuHelperList:
        printT(
            f"Current chapter for novel {syosetuHelper.name}: {syosetuHelper.latest_chapter_title} ({syosetuHelper.translateUrl})"
        )
        schedule.every(5).to(30).minutes.do(
            syosetuChecker,
            syosetuHelper=syosetuHelper,
            show_no_update_msg=False,
        )

    while True:
        schedule.run_pending()
        time.sleep(1)
