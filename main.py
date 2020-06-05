import wutuxs.check_chapter
# import ohmanhua.check_chapter
from tg.bot import send_channel
import wutuxs.check_chapter as wutuxs
import time

loop_switch = True
current_chapter_title = None

def check_wutuxs():
    # global loop_switch
    global current_chapter_title

    latest_chapter_url, latest_chapter_title = wutuxs.getLatestChapter()

    if latest_chapter_title != current_chapter_title:

        print("Update found!")

        latest_chapter_content = wutuxs.getContent(url=latest_chapter_url)

        content = "<u><b>%s</b></u>\n\n%s" % (latest_chapter_title, latest_chapter_content)

        # send_channel(content)
        send_channel(latest_chapter_url)

        # loop_switch = False
        current_chapter_title = latest_chapter_title
    else:
        print(getTime(), "No update found")

def getTime():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

def withinCheckPeriod():
    start_hour = 18
    end_hour = 23
    t = time.localtime()
    current_hour = time.strftime("%H", t)
    return start_hour <= int(current_hour) <= end_hour

if __name__ == '__main__':
    print(getTime(), "Program Start!")

    # send_channel("Program Start!")

    starttime = time.time()

    current_chapter_url, current_chapter_title = wutuxs.getLatestChapter()
    print(getTime(), "Current chapter: ", current_chapter_title)

    while loop_switch:

        if withinCheckPeriod():
            print(getTime(), "checking")
            check_wutuxs()
        
        # sleep for 1min
        if loop_switch:
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
        
    print(getTime(), "Program end")
