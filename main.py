import os
import time
from dotenv import load_dotenv
import helpers.wutuxs.check_chapter as wutuxs
from helpers.functions import *
from helpers.TgHelper import TgHelper

load_dotenv()

current_chapter_title = None
start_hour = 18
end_hour = 22

show_no_update_msg = False


def check_wutuxs(token, chat_id):
    global current_chapter_title
    tgHelper = TgHelper(token, chat_id)

    latest_chapter_url, latest_chapter_title = wutuxs.getLatestChapter()

    if latest_chapter_title is not None:
        if latest_chapter_title != current_chapter_title:

            printT("Update found! {}".format(latest_chapter_title))

            # latest_chapter_content = wutuxs.getContent(url=latest_chapter_url)

            # content = "<u><b>{}</b></u>\n\n{}".format(
            #     latest_chapter_title, latest_chapter_content
            # )

            # send_channel(content)
            novel_title = "元尊"
            content = "novel <<{}>> updated!".format(novel_title)
            url_text = "<<{}>> {}".format(novel_title, latest_chapter_title)
            tgHelper.send_channel(
                content=content,
                url_text=url_text,
                url=latest_chapter_url,
            )

            current_chapter_title = latest_chapter_title
        else:
            if show_no_update_msg:
                printT("No update found")


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

    token = os.environ.get("TOKEN", "<your token>")
    chat_id = os.environ.get("CHAT_ID", "<your chat_id>")

    starttime = time.time()

    current_chapter_url, current_chapter_title = wutuxs.getLatestChapter()
    printT("Current chapter: {}".format(current_chapter_title))

    while True:
        # check once per minute
        if withinCheckPeriod(start_hour, end_hour):
            check_wutuxs(token, chat_id)

        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
