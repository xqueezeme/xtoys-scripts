import json
import operator
import os
import time
from datetime import datetime, date

import chromedriver_binary_sync
import cloudscraper
import requests
from fake_useragent import UserAgent
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from tqdm import tqdm

from modules import validation_service, post_service, image_service
from modules.common import CustomDecoder, CustomEncoder
from modules.image_service import image_folder

chromedriver_binary_sync.download()

display = Display(visible=0, size=(800, 600))
display.start()

xpath_invalid_spankbang = "//*[contains(text(),'deze video is niet langer beschikbaar.')]"
xpath_invalid_pornhubs = ["//*[contains(text(), 'Fout Pagina Niet Gevonden')]",
                          "//*[contains(text(), 'Gratis Premium Video')]",
                          "//*[contains(text(), 'Video werd verwijderd')]",
                          "//*[contains(text(), 'Deze video werd uitgeschakeld')]",
                          "//*[contains(text(), 'Video is disabled')]"]
ua = UserAgent()
userAgent = str(ua.random)
session = requests.Session()
f = open('./credentials.json')
credentials = json.load(f)
options = webdriver.ChromeOptions()
options.add_argument("--mute-audio")
options.add_argument('--disable-browser-side-navigation')
options.add_argument("--headless")

driver = webdriver.Chrome(options=options)
scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance

import re

def getPage(url):
    try:
        response = session.get(url)
        return response.text
    except:
        print('Error trying to access ' + url + '\nTrying again in 10 sec')
        time.sleep(5)
        return getPage(url)


def seleniumLogin():
    driver.get('https://pornhub.com')
    driver.implicitly_wait(5)

    driver.get('https://discuss.eroscripts.com/login')
    driver.implicitly_wait(5)
    input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-account-name"))
    )
    # Type in text in input field.
    input.send_keys(credentials['username'])
    input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-account-password"))
    )
    # Type in text in input field.
    input.send_keys(credentials['password'])
    ##################################

    input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-button"))
    )
    input.click()
    # Pause for 10 seconds so that you can see the results.
    time.sleep(10)
    cookies = {}
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie['name']] = cookie['value']
    session.cookies.update(cookies)

titleEscapeWords = ['pack']


def read_infiniscroll(by, url, pages):
    newTopics = []
    for i in tqdm(range(pages),
                  desc="Reading " + by + " topics",
                  ascii=False, ncols=75):
        if (i == 0):
            scrollJson = getPage(url)
        else:
            scrollJson = getPage(url + '&page=' + str(i))
        data = json.loads(scrollJson)
        if (data):
            topicsUsers = data.get('users')
            topicList = data.get('topic_list')
            if topicList:
                topics = topicList.get('topics')
                if len(topics) > 0:
                    for topic in topics:
                        username = ''
                        if (topicsUsers):
                            originalPoster = next(
                                filter(lambda poster: poster.get('description').__contains__('Original Poster'),
                                       topic.get('posters')), None)
                            if (originalPoster):
                                user = next(
                                    filter(lambda user: user.get('id') == originalPoster.get('user_id'), topicsUsers),
                                    None)
                                if (user):
                                    username = user.get('username')
                        title = topic.get('title', None)
                        if title:
                            newTopics.append({'url': 'https://discuss.eroscripts.com/t/' + topic.get(
                                'slug') + '/' + str(topic.get('id')),
                                              'title': title,
                                              'slug': topic.get('slug'),
                                              'created_at': topic.get('created_at'),
                                              'tags': topic.get('tags'),
                                              'username': username,
                                              'pack': next(filter(lambda keyword: title.lower().__contains__(keyword),
                                                                  titleEscapeWords), None) == None
                                              })
                else:
                    break
            else:
                break
        else:
            break

    return list(reversed(newTopics))


def upgradeScript(sourceIndexFile, modelVersion):
    if os.path.exists(sourceIndexFile):
        f = open(sourceIndexFile)
        data = json.load(f)
    else:
        data = {}
        data['author'] = 'xqueezeme'
        data['videos'] = []
    data['version'] = modelVersion
    videos = data['videos']
    newVideos = []
    for idx in tqdm(range(len(videos)),
                    desc="Upgrading script videos",
                    ascii=False, ncols=75):
        video = videos[idx]
        if datetime.today().day == 1:
            video['ignore'] = False
            video['valid'] = True

        if (not video.get('ignore', False)):
            scripts = []
            if video.get('script'):
                scripts.append({"name": '', "location": video['script']})
                video['scripts'] = scripts
                video.pop('script', None)
        if video.get('thumbnail-data', None):
           del video['thumbnail-data']
        filename = image_service.slugify(video['name']) + '.jpeg'
        if not video.get('thumbnail') and os.path.exists(image_folder + '/' + filename):
            video['thumbnail'] = 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + image_folder + '/' + filename

        newVideos.append(video)
    data['videos'] = newVideos
    jsonStr = json.dumps(data, indent=4)
    with open(sourceIndexFile, "w") as outfile:
        outfile.write(jsonStr)


def createDisplayName(name):
    keywords = ['request filled', 'request fulfillment', 'completed request', 'script requested', 'script request',
                'first script', 'pornhub', 'request']
    for keyword in keywords:
        name = re.sub('[\(]\s*' + keyword + '\s*\[\)]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub('[\[]\s*' + keyword + '\s*\]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub('\s*' + keyword + '\s*[\:]?[\-]?\s*', '', name, flags=re.IGNORECASE)
    return name.strip()


def save_index(sourceIndexFile, indexFileName):
    if os.path.exists(sourceIndexFile):
        with open(sourceIndexFile) as f:
            data = json.load(f)
    else:
        data = {}
        data['author'] = 'xqueezeme'
        data['videos'] = []
        data['tags'] = []
    data['version'] = modelVersion
    videos = data['videos']
    newVideos = []
    tags = {}
    print("Upgrading script videos")
    for idx, video in enumerate(videos):
        if (video.get('ignore', False) == False and video.get('valid', True)):
            video['displayName'] = createDisplayName(video.get('name'))
            for tag in video['tags']:
                newTags = tags.get(tag)
                if (newTags == None):
                    newTags = []
                newTags.append(video['name'])
                tags[tag] = newTags
            newVideos.append(video)
    print(f"Active videos: {len(newVideos)}")
    data['videos'] = newVideos
    data['tags'] = dict(sorted(tags.items(), key=operator.itemgetter(0)))

    jsonStr = json.dumps(data)
    with open(indexFileName, "w") as outfile:
        outfile.write(jsonStr)



def loop_topics(sourceIndexFile, topics):
    ignoreUrls = []
    if os.path.exists('ignore-urls.json'):
        f = open('ignore-urls.json')
        ignoreIndex = json.load(f)
        ignoreUrls = list(set(ignoreIndex.get('urls')))
    else:
        ignoreIndex = {}

    with open(sourceIndexFile) as f:
        data = json.load(f, cls=CustomDecoder)
        videos = data['videos']
        filtered_topics = list(filter(lambda t: t.get('url') not in ignoreUrls, topics))
        videosAdded = 0
        for idx in tqdm(range(len(filtered_topics)),
                        desc="Getting videos from topics",
                        ascii=False, ncols=75):
            topic = filtered_topics[idx]
            if not topic['url'] in ignoreUrls:
                matchingVideo = next(filter(lambda existing: existing['name'] == topic['title'], videos), None)
                if (matchingVideo):
                    matchingVideo['tags'] = topic['tags']
                    matchingVideo['creator'] = topic['username']
                    matchingVideo['created_at'] = topic['created_at']
                else:
                    url = topic['url']
                    print(f"Parsing page for {url}")
                    newvideos = post_service.parse_page_from_url(url, topic, session, driver)
                    if newvideos and len(newvideos) > 0:
                        for video in newvideos:
                            if video:
                                existingVideo = next(filter(
                                    lambda existing: existing['id'] == video['id'] and existing['site'] == video[
                                        'site'], videos), None)
                                if (existingVideo == None):
                                    videos.append(video)
                                    videosAdded += 1
                                else:
                                    existingVideo['tags'] = video['tags']
                                    existingVideo['creator'] = video['creator']
                                    existingVideo['created_at'] = video['created_at']

                            else:
                                ignoreUrls.append(topic['url'])
                    else:
                        ignoreUrls.append(topic['url'])

            data['videos'] = videos
            jsonStr = json.dumps(data, indent=4, cls=CustomEncoder)
            with open(sourceIndexFile, "w") as outfile:
                outfile.write(jsonStr)

            ignoreIndex['urls'] = ignoreUrls
            jsonStr = json.dumps(ignoreIndex, indent=4)
            with open('ignore-urls.json', "w") as outfile:
                outfile.write(jsonStr)

    return videosAdded


def savePage(page, url):
    pageContent = getPage(url)
    with open(page, "w") as outfile:
        outfile.write(pageContent)


sourceIndexFile = 'index-source.json'
indexFile = 'index.json'
modelVersion = 1

validation_service.validate_selenium(driver, sourceIndexFile, all=True)

save_index(sourceIndexFile, indexFile)