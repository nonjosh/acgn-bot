import os
import time
import schedule
import json
from dotenv import load_dotenv
from helpers import printT, TgHelper, CocomanhuaHelper, WutuxsHelper, ManhuaguiHelper

load_dotenv()
token = os.environ.get("TOKEN", "<your token>")
chat_id = os.environ.get("CHAT_ID", "<your chat_id>")

# start_hour = 18
# end_hour = 22


def wutuxsChecker(wutuxsHelper, show_no_update_msg=False):
    novel_name = wutuxsHelper.name
    if wutuxsHelper.checkUpdate():
        printT(
            f"Update found for {wutuxsHelper.name}: {wutuxsHelper.latest_chapter_title} ({wutuxsHelper.latest_chapter_url})"
        )

        tgHelper = TgHelper(token, chat_id)
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

        tgHelper = TgHelper(token, chat_id)
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

        tgHelper = TgHelper(token, chat_id)
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


if __name__ == "__main__":

    printT("Program Start!")

    # printT("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    with open("list.json") as f:
        data = json.load(f)

    cocomanhuaHelperList = []
    wutuxsHelperList = []
    manhuaguiHelperList = []
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

    while True:
        schedule.run_pending()
        time.sleep(1)
