import os
import time
from dotenv import load_dotenv
import schedule
from helpers import printT, TgHelper, CocomanhuaHelper, WutuxsHelper

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


if __name__ == "__main__":

    printT("Program Start!")

    # printT("Check hour range: {}:00:00 - {}:00:00".format(start_hour, end_hour))

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
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="修真聊天群", url="https://www.cocomanhua.com/10268/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="石紀元", url="https://www.cocomanhua.com/14424/")
    )
    cocomanhuaHelperList.append(
        CocomanhuaHelper(name="元尊", url="https://www.cocomanhua.com/10136/")
    )

    wutuxsHelperList = []
    wutuxsHelperList.append(
        WutuxsHelper(name="元尊", url="http://www.wutuxs.com/html/7/7876/")
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

    while True:
        schedule.run_pending()
        time.sleep(1)
