import wutuxs.check_chapter
# import ohmanhua.check_chapter
from tg.bot import send_channel
import wutuxs.check_chapter as wutuxs
import time

current_chapter_title = None
start_hour = 18
end_hour = 22

def check_wutuxs():
    global current_chapter_title

    latest_chapter_url, latest_chapter_title = wutuxs.getLatestChapter()

    if latest_chapter_title != current_chapter_title:

        print("Update found!")

        latest_chapter_content = wutuxs.getContent(url=latest_chapter_url)

        content = "<u><b>%s</b></u>\n\n%s" % (latest_chapter_title, latest_chapter_content)

        # send_channel(content)
        send_channel(latest_chapter_url)

        current_chapter_title = latest_chapter_title
    else:
        print(getTime(), "No update found")

def getTime():
    t = time.localtime()
    current_time = time.strftime("%H:%M:%S", t)
    return current_time

def withinCheckPeriod():
    t = time.localtime()
    current_hour = time.strftime("%H", t)
    return start_hour <= int(current_hour) <= end_hour

if __name__ == '__main__':
    
    print(getTime(), "Program Start!")
    print("Check hour range: %s:00:00 - %s:00:00" % (start_hour, end_hour))

    # send_channel("Program Start!")

    starttime = time.time()

    current_chapter_url, current_chapter_title = wutuxs.getLatestChapter()
    print(getTime(), "Current chapter: ", current_chapter_title)

    while True:

        if withinCheckPeriod():
            check_wutuxs()
        
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
