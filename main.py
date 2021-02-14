import os
import time
from dotenv import load_dotenv
import schedule
import helpers.wutuxs.check_chapter as wutuxs
from helpers.functions import *
from helpers.TgHelper import TgHelper
from helpers.CocomanhuaHelper import CocomanhuaHelper

load_dotenv()
token = os.environ.get("TOKEN", "<your token>")
chat_id = os.environ.get("CHAT_ID", "<your chat_id>")

current_chapter_title = None
start_hour = 18
end_hour = 22


def check_wutuxs(token, chat_id, show_no_update_msg=False):
    global current_chapter_title
    tgHelper = TgHelper(token, chat_id)

    latest_chapter_url, latest_chapter_title = wutuxs.getLatestChapter()

    if latest_chapter_title is not None:
        novel_title = "元尊"
        if latest_chapter_title != current_chapter_title:

            printT(f"Update found for {latest_chapter_title}!")

            # latest_chapter_content = wutuxs.getContent(url=latest_chapter_url)

            # content = "<u><b>{}</b></u>\n\n{}".format(
            #     latest_chapter_title, latest_chapter_content
            # )

            # send_channel(content)
            content = f"novel <<{novel_title}>> updated!"
            url_text = f"<<{novel_title}>> {latest_chapter_title}"
            tgHelper.send_channel(
                content=content,
                url_text=url_text,
                url=latest_chapter_url,
            )

            current_chapter_title = latest_chapter_title
        else:
            if show_no_update_msg:
                printT(f"No update found for {novel_title}")


def cocomanhuaChecker(cocomanhuaHelper, show_no_update_msg=False):
    comic_title = cocomanhuaHelper.name
    if cocomanhuaHelper.checkUpdate():
        printT(f"Update found for {cocomanhuaHelper.latest_chapter_title}")

        tgHelper = TgHelper(token, chat_id)
        content = f"comic <<{comic_title}>> updated!"
        url_text = f"<<{comic_title}>> {cocomanhuaHelper.latest_chapter_title}"
        tgHelper.send_channel(
            content=content,
            url_text=url_text,
            url=cocomanhuaHelper.latest_chapter_url,
        )
    else:
        if show_no_update_msg:
            printT(f"No update found for {comic_title}")


if __name__ == "__main__":

    printT("Program Start!")

    # TODO multiprocess to handle different website checker
    printT("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    # send_channel("Program Start!")
    # send_channel(
    #     content="<<元尊>> updates:",
    #     url_text="第一千三百一十四章 追逃",
    #     url="http://www.wutuxs.com/html/7/7876/7787923.html",
    # )

    starttime = time.time()

    current_chapter_url, current_chapter_title = wutuxs.getLatestChapter()
    printT(f"Current chapter: {current_chapter_title}")

    cocomanhuaHelperList = []

    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="萬古神王", url="https://www.cocomanhua.com/12970/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="放開那個女巫", url="https://www.cocomanhua.com/12394/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="撿個校花做老婆", url="https://www.cocomanhua.com/12457/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="萬古神王", url="https://www.cocomanhua.com/12970/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="總之就是非常可愛", url="https://www.cocomanhua.com/15006/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="我家大師兄腦子有坑", url="https://www.cocomanhua.com/10994/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="仙帝歸來", url="https://www.cocomanhua.com/12650/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="碧藍之海", url="https://www.cocomanhua.com/15010/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="失業魔王", url="https://www.cocomanhua.com/13657/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="英雄？我早就不當了", url="https://www.cocomanhua.com/10291/")
    )

    for cocomanhuaHelper in cocomanhuaHelperList:
        schedule.every(5).to(30).minutes.do(
            cocomanhuaChecker,
            cocomanhuaHelper=cocomanhuaHelper,
            show_no_update_msg=False,
        )
    # schedule.every(1).to(10).seconds.do(
    #     check_wutuxs, token=token, chat_id=chat_id, show_no_update_msg=True
    # )

    while True:
        schedule.run_pending()
        time.sleep(1)
    #     # check once per minute
    #     if withinCheckPeriod(start_hour, end_hour):
    #         check_wutuxs(token, chat_id)
    #     time.sleep(60.0 - ((time.time() - starttime) % 60.0))
