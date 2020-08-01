import requests
from bs4 import BeautifulSoup
from hanziconv import HanziConv
import helpers.wutuxs.config as config

url = config.main_url + '/html/7/7876/index.html'

# def getsoup():
#     # Connect to the URL
#     response = requests.get(url)

#     response.encoding = 'gb18030'

#     soup = BeautifulSoup(response.text, 'html.parser')

#     return soup

# TODO rewrite to OOP
def getLatestChapter():
    # Connect to the URL
    response = requests.get(url)

    response.encoding = 'gb18030'

    soup = BeautifulSoup(response.text, 'html.parser')

    a_tags = soup.findAll('a')

    chapter_list = []
    for i in range(0, len(a_tags)-1):  # 'a' tags are for links
        one_a_tag = a_tags[i]

        try:
            link = one_a_tag['href']
            if link.startswith('/html/'):
                chapter_title = one_a_tag.string
                chapter_list.append((link, chapter_title))
        except KeyError:
            pass

    # Get latest content
    latest_chapter_url, latest_chapter_title = chapter_list[-1]
    latest_chapter_url = config.main_url + latest_chapter_url

    return latest_chapter_url, latest_chapter_title

# def getLatestChapter(soup):
#     a_tags = soup.findAll('a')

#     chapter_list = []
#     for i in range(0, len(a_tags)-1):  # 'a' tags are for links
#         one_a_tag = a_tags[i]

#         try:
#             link = one_a_tag['href']
#             if link.startswith('/html/'):
#                 chapter_title = one_a_tag.string
#                 chapter_list.append((link, chapter_title))
#         except KeyError:
#             pass

#     # Get latest content
#     latest_chapter_url, latest_chapter_title = chapter_list[-1]
#     latest_chapter_url = config.main_url + latest_chapter_url

#     return latest_chapter_url, latest_chapter_title

def getContent(url):
    # Connect to the URL
    response = requests.get(url)

    response.encoding = 'gb18030'

    soup = BeautifulSoup(response.text, 'html.parser')

    content = soup.find(id='contents').text

    content = HanziConv.toTraditional(content)

    return content

# # Connect to the URL
# response = requests.get(url)

# response.encoding = 'gb18030'

# soup = BeautifulSoup(response.text, 'html.parser')

# a_tags = soup.findAll('a')

# chapter_list = []
# for i in range(0, len(a_tags)-1):  # 'a' tags are for links
#     one_a_tag = a_tags[i]

#     try:
#         link = one_a_tag['href']
#         if link.startswith('/html/'):
#             chapter_title = one_a_tag.string
#             chapter_list.append((link, chapter_title))
#     except KeyError:
#         pass

# # Get latest content
# latest_chapter_url, latest_chapter_title = chapter_list[-1]
# latest_chapter_url = config.main_url + latest_chapter_url

# # print(latest_chapter_title)

# # Connect to the URL
# response = requests.get(latest_chapter_url)

# response.encoding = 'gb18030'

# soup = BeautifulSoup(response.text, 'html.parser')

# content = soup.find(id='contents').text

# content = HanziConv.toTraditional(content)

# print(content)