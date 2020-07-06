from helpers.tg.bot import send_channel
import helpers.wutuxs.check_chapter as wutuxs
import time

current_chapter_title = None
start_hour = 18
end_hour = 22

def check_wutuxs():
    global current_chapter_title

    latest_chapter_url, latest_chapter_title = wutuxs.getLatestChapter()

    if latest_chapter_title != current_chapter_title:

        printT('Update found! {}'.format(latest_chapter_title))

        latest_chapter_content = wutuxs.getContent(url=latest_chapter_url)

        content = '<u><b>{}</b></u>\n\n{}'.format(latest_chapter_title, latest_chapter_content)

        # send_channel(content)
        send_channel(latest_chapter_url)

        current_chapter_title = latest_chapter_title
    else:
        printT('No update found')

def getTime():
    t = time.localtime()
    current_time = time.strftime('%H:%M:%S', t)
    return current_time

def printT(msg):
    print('[{}] {}'.format(getTime(), msg))


def withinCheckPeriod():
    t = time.localtime()
    current_hour = time.strftime('%H', t)
    return start_hour <= int(current_hour) <= end_hour

if __name__ == '__main__':
    
    printT('Program Start!')
    printT('Check hour range: %s:00:00 - %s:00:00' % (start_hour, end_hour))

    # send_channel("Program Start!")

    starttime = time.time()

    current_chapter_url, current_chapter_title = wutuxs.getLatestChapter()
    printT('Current chapter: {}'.format(current_chapter_title))

    while True:

        if withinCheckPeriod():
            check_wutuxs()
        
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))
