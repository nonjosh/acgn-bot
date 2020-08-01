from helpers.tg.bot import send_channel
import helpers.wutuxs.check_chapter as wutuxs
from datetime import datetime
import time

current_chapter_title = None
start_hour = 18
end_hour = 22


def check_wutuxs():
    global current_chapter_title

    latest_chapter_url, latest_chapter_title = wutuxs.getLatestChapter()

    if latest_chapter_title != current_chapter_title:

        printT("Update found! {}".format(latest_chapter_title))

        latest_chapter_content = wutuxs.getContent(url=latest_chapter_url)

        content = "<u><b>{}</b></u>\n\n{}".format(
            latest_chapter_title, latest_chapter_content
        )

        # send_channel(content)
        send_channel(latest_chapter_url)

        current_chapter_title = latest_chapter_title
    else:
        printT('No update found')
        return


def getDateTime():
    now = datetime.now()
    current_time = now.strftime("%Y/%m/%d %H:%M:%S")
    return current_time


def printT(msg):
    print("[{}] {}".format(getDateTime(), msg))


def withinCheckPeriod():
    now = datetime.now()
    current_hour = now.strftime("%H")
    return start_hour <= int(current_hour) <= end_hour


if __name__ == "__main__":

    printT("Program Start!")

    # TODO multiprocess to handle different website checker
    printT("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

    # send_channel("Program Start!")

    starttime = time.time()

    current_chapter_url, current_chapter_title = wutuxs.getLatestChapter()
    printT("Current chapter: {}".format(current_chapter_title))

    while True:

        if withinCheckPeriod():
            check_wutuxs()

        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
