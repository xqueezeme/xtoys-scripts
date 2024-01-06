import base64
import operator
import random
from datetime import datetime, date, timedelta
from io import BytesIO

from bs4 import BeautifulSoup as Soup

import re
import requests
from fake_useragent import UserAgent
import time
import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import lxml.etree as etree
import json
from tqdm import tqdm
import traceback
import os
import sys
from pyvirtualdisplay import Display
import cloudscraper

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
image_folder = 'images'

import unicodedata
import re

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

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


def download_file(filename, url, retries=0):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    retries += 1
    try:
        with session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
        return local_filename
    except:
        if (retries < 5):
            print('Error trying to download ' + url + '\nTrying again in 10 sec')
            time.sleep(5)
            return download_file(filename, url, retries=retries)
        else:
            return None


def getSpankbangId(url):
    regex = re.compile(r'spankbang.com\/([a-zA-Z0-9]+)\/video')
    return regex.search(url)[1]


def getPornhubId(url):
    regex = re.compile(r'viewkey=([a-z0-9]+)')
    return regex.search(url)[1]


def getXvideosId(url):
    regex = re.compile(r'\/video(\d+)\/')
    return regex.search(url)[1]


def getXhamsterId(url):
    regex = re.compile(r'xhamster\.com\/videos\/(.*)\/?.*')
    group = regex.search(url)[1]
    split = group.split('-')
    return split[len(split) - 1]


def getEpornerId(url):
    regex = re.compile(r'Eporner\.com\/video\-([a-zA-Z0-9]+)\/?.*')
    group = regex.search(url)
    if (group):
        return group[1]
    regex = re.compile(r'Eporner\.com\/.*\/([a-zA-Z0-9]+)\/.*')
    return regex.search(url)[1]


def getUrl(site, id):
    if (site == 'pornhub'):
        return 'https://nl.pornhub.com/view_video.php?viewkey=' + id
    elif (site == 'spankbang'):
        return 'https://nl.spankbang.com/' + id + '/video/test'
    elif (site == 'xvideos'):
        return 'https://www.xvideos.com/video' + id + '/xxx'
    elif (site == 'xhamster'):
        return 'https://nl.xhamster.com/videos/xxx-' + id
    elif (site == 'eporner'):
        return 'https://www.eporner.com/video-' + id + '/'

    return None


def findPornhubIds(pornhubSel):
    links = []
    if (len(pornhubSel) > 0):
        for a in pornhubSel:
            if (not str(a).__contains__('pornhub.com/pornstar/') and not str(a).__contains__(
                    'pornhub.com/model/') and not str(a).__contains__('pornhub.com/users/') and not str(a).__contains__(
                    'pornhub.com/playlist/') and not str(a).__contains__('pornhub.com/channels/')):
                try:
                    id = getPornhubId(str(a))
                    if (id):
                        links.append(id)
                except:
                    pass
    return list(map(lambda link: {'id': link, 'site': 'pornhub'}, set(links)))


def findSpankbangIds(spankbangSel):
    links = []
    if (len(spankbangSel) > 0):
        for a in spankbangSel:
            if (not str(a).__contains__('/playlist/') and not str(a).__contains__('/profile/')):
                try:
                    id = getSpankbangId(str(a))
                    if (id):
                        links.append(id)

                except:
                    pass
    return list(map(lambda link: {'id': link, 'site': 'spankbang'}, set(links)))


def findXvideosIds(xvideosSel):
    links = []
    if (len(xvideosSel) > 0):
        for a in xvideosSel:
            if (not str(a).__contains__('/profiles/')):
                try:
                    id = getXvideosId(str(a))
                    if (id):
                        links.append(id)
                except:
                    pass
    return list(map(lambda link: {'id': link, 'site': 'xvideos'}, set(links)))


def findXhamsterIds(xhamsterSel):
    links = []
    if (len(xhamsterSel) > 0):
        for a in xhamsterSel:
            try:
                id = getXhamsterId(str(a))
                if (id):
                    links.append(id)
            except:
                pass
    return list(map(lambda link: {'id': link, 'site': 'xhamster'}, set(links)))


def findEpornerIds(EpornerSel):
    links = []
    if (len(EpornerSel) > 0):
        for a in EpornerSel:
            try:
                id = getEpornerId(str(a))
                if (id):
                    links.append(id)
            except:
                pass
    return list(map(lambda link: {'id': link, 'site': 'eporner'}, set(links)))


epornerAXPath = './/a[contains(@href,"Eporner.com")]/@href'
spankbangAXPath = './/a[contains(@href,"spankbang.com")]/@href'
pornhubAXPath = './/a[contains(@href,"pornhub.com")]/@href'
xvideosAXPath = './/a[contains(@href,"xvideos.com")]/@href'
xhamsterAXPath = './/a[contains(@href,"xhamster.com")]/@href'


def findVideoLinks(element):
    newVideoLinks = []
    spankbangSel = element.xpath(spankbangAXPath)
    newVideoLinks = newVideoLinks + findSpankbangIds(spankbangSel)

    pornhubSel = element.xpath(pornhubAXPath)
    newVideoLinks = newVideoLinks + findPornhubIds(pornhubSel)

    xvideosSel = element.xpath(xvideosAXPath)
    newVideoLinks = newVideoLinks + findXvideosIds(xvideosSel)
    xhamsterSel = element.xpath(xhamsterAXPath)
    newVideoLinks = newVideoLinks + findXhamsterIds(xhamsterSel)
    EpornerSel = element.xpath(epornerAXPath)
    newVideoLinks = newVideoLinks + findEpornerIds(EpornerSel)
    return newVideoLinks


def parsePost(post, topic, funscriptsFolder):
    newVideoLinks = findVideoLinks(post)
    funscripts = []
    regexpNS = 'http://exslt.org/regular-expressions'
    links = post.xpath(".//*[not(blockquote)]//a[re:test(@href, '(\.funscript$)')]", namespaces={'re': regexpNS})

    for link in links:
        if (link.get("href").startswith('http')):
            funscripts.append({'location': link.get("href"), 'name': ''.join(link.itertext())})
        else:
            funscripts.append(
                {'location': 'https://discuss.eroscripts.com' + link.get("href"), 'name': ''.join(link.itertext())})

    if (len(newVideoLinks) == 1 and len(funscripts) > 0 and len(funscripts) <= 3):
        id = newVideoLinks[0]
        if (id):
            funscriptIndex = 1
            scripts = []
            allscriptsfound = True
            for funscript in funscripts:
                filename = topic['slug'] + '-' + str(funscriptIndex) + '.funscript'
                if (not os.path.exists(funscriptsFolder + '/' + filename)):
                    file = download_file(funscriptsFolder + '/' + filename, funscript['location'])
                    if (file == None):
                        allscriptsfound = False
                scripts.append({'name': funscript['name'],
                                'location': 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + funscriptsFolder + '/' + filename})
                funscriptIndex += 1
            if (allscriptsfound):
                video = {
                    "name": topic['title'],
                    "site": id['site'],
                    "id": id['id'],
                    "scripts": scripts,
                    "tags": topic['tags'],
                    "created_at": topic['created_at'],
                    "url": topic['url'],
                    "valid": True,
                    "creator": topic['username'],
                    "ignore": False
                }
                validateVideo(video)
                return video
            else:
                return None
        return None


def parsePack(post):
    current = ''
    title = None
    link = None
    funscripts = None
    videos = []
    for el in post:
        text = ''.join(el.itertext()).strip().lower()
        if (text):
            if (current == 'title'):
                title = text.split('\n')[0]
                current = None
            elif (current == 'link'):
                videoLinks = findVideoLinks(el)
                current = None

            elif (current == 'script'):
                regexpNS = 'http://exslt.org/regular-expressions'
                funscripts = []
                links = el.xpath(".//a[re:test(@href, '(\.funscript$)')]", namespaces={'re': regexpNS})
                if (len(links) > 0):
                    for link in links:
                        if (link.get("href").startswith('http')):
                            funscripts.append({'location': link.get("href"), 'name': ''.join(link.itertext())})
                        else:
                            funscripts.append({'location': 'https://discuss.eroscripts.com' + link.get("href"),
                                               'name': ''.join(link.itertext())})
                    current = None
                if (title and funscripts != None and len(funscripts) > 0 and videoLinks != None and len(
                        videoLinks) == 1):
                    video = videoLinks[0]
                    if (title.lower() == 'length'):
                        title = funscripts[0]['name'].replace('.funscript', '')
                    videos.append({'title': title, 'site': video['site'], 'id': video['id'], 'funscripts': funscripts})
                title = None
                link = None
                funscripts = None
                videoLinks = None


            elif (text == 'details'):
                current = 'title'
            elif (text == 'video link') or el.get('alt') == ':movie_camera:':
                current = 'link'
            elif (text == 'script'):
                current = 'script'
        if el.tag == 'hr':
            if (title and funscripts != None and len(funscripts) > 0 and videoLinks != None and len(videoLinks) == 1):
                video = videoLinks[0]
                if (title.lower() == 'length'):
                    title = funscripts[0]['name'].replace('.funscript', '')
                videos.append({'title': title, 'site': video['site'], 'id': video['id'], 'funscripts': funscripts})
            title = None
            link = None
            funscripts = None
            videoLinks = None
    return videos


def parsePage(text, topic, funscriptsFolder):
    soup = Soup(text, "lxml")
    dom = etree.HTML(str(soup))
    posts = dom.xpath('//div[contains(@itemprop,"articleBody")]')
    videos = []
    if (len(posts) > 0):
        post = posts[0]
        postId = post.xpath('.//*')
        if (len(post.xpath('.//hr')) > 0 or len(post.xpath(".//h3[text() =' Details']")) > 1):
            packVideos = parsePack(posts)
            for video in packVideos:
                funscriptIndex = 1
                scripts = []
                allscriptsfound = True
                for funscript in video['funscripts']:
                    filename = topic['slug'] + '-' + video['id'] + '-' + str(funscriptIndex) + '.funscript'
                    if (not os.path.exists(funscriptsFolder + '/' + filename)):
                        file = download_file(funscriptsFolder + '/' + filename, funscript['location'])
                        if (file == None):
                            allscriptsfound = False
                    scripts.append({'name': funscript['name'],
                                    'location': 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + funscriptsFolder + '/' + filename})
                    funscriptIndex += 1
                if allscriptsfound:
                    video = {
                        "name": video['title'],
                        "site": video['site'],
                        "id": video['id'],
                        "scripts": scripts,
                        "tags": topic['tags'],
                        "created_at": topic['created_at'],
                        "url": topic['url'],
                        "valid": True,
                        "creator": topic['username'],
                        "ignore": False,
                        "pack": True
                    }
                    validateVideo(video)
                    videos.append(video)
                else:
                    return None
        else:
            video = parsePost(post, topic, funscriptsFolder)
            if video:
                videos.append(video)
    return videos


def formatHTML(content):
    start = content.index('<body')
    end = content.index('</body>')
    return '<!DOCTYPE html><html lang="en">' + content[start: end - 1] + '</body></html'


titleEscapeWords = ['pack']


def readInfiniscroll(by, url, pages):
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
    return newTopics


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
        newVideos.append(video)
    data['videos'] = newVideos
    jsonStr = json.dumps(data, indent=4)
    with open(sourceIndexFile, "w") as outfile:
        outfile.write(jsonStr)


def createDisplayName(name):
    keywords = ['request filled', 'request fulfillment', 'completed request', 'script requested', 'script request',
                'first script', 'pornhub', 'request'];
    for keyword in keywords:
        name = re.sub('[\(]\s*' + keyword + '\s*\[\)]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub('[\[]\s*' + keyword + '\s*\]\s*', '', name, flags=re.IGNORECASE)
        name = re.sub('\s*' + keyword + '\s*[\:]?[\-]?\s*', '', name, flags=re.IGNORECASE)
    return name.strip()


def saveIndex(sourceIndexFile, indexFileName):
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


def validateSelenium(sourceIndexFile):
    data = None
    with open(sourceIndexFile) as file:
        data = json.load(file, cls=CustomDecoder)
    if data:
        videos = data['videos']
        videos_to_validate = list(filter(lambda v:
                                         not v.get('ignore', False) and
                                         (v.get('last_checked') is None or v.get(
                                             'last_checked') < datetime.utcnow() - timedelta(days=7))
                                         , videos))
        for count, video in enumerate(videos_to_validate):
            print(f"Validating video {count} / {len(videos_to_validate)}")
            if video.get('image-data'):
                del video["image-data"]

            validateVideo(video)
            data['videos'] = videos
            jsonStr = json.dumps(data, indent=4, cls=CustomEncoder)
            with open(sourceIndexFile, "w") as outfile:
                outfile.write(jsonStr)


scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
import requests
from PIL import Image


def pillow_image_to_base64_string(img):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    return 'data:image/jpeg;base64,' + base64.b64encode(buffered.getvalue()).decode("utf-8")


def create_image_data_url(url):

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    size = 256, 256
    img.thumbnail(size, Image.Resampling.LANCZOS)

    return pillow_image_to_base64_string(img)


def update_img(video, image_link, filename):
    if image_link:
      if not os.path.exists(image_folder + '/' + filename):
        data_url = create_image_data_url(image_link)
        if data_url:
            video['thumbnail'] = 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + image_folder + '/' + filename
            print(f"Updating thumbnail {video['name']}")
    
            with open(image_folder + "/" + filename, "w") as outfile:
              outfile.write(data_url)

def get_image(driver, site, video):
    filename = slugify(video['name']) + '.jpeg'
    try:
        if site == "eporner":
            image_xpath = "//*[@id=''moviexxx']/div[@poster]"

            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:
                image_link = img.get_attribute("poster")
                update_img(video, image_link, filename)
                return True
        elif site == "pornhub":
            image_xpath = '//*[@id="player"]//img'
            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:
                update_img(video, img.get_attribute("src"), filename)
                return True

        elif site == "xvideos":
            image_xpath = '//*[@class="video-pic"]/img'
            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:
                update_img(video, img.get_attribute("src"), filename)
                return True

        elif site == "xhamster":
            image_xpath = '//*[@class="xp-preload-image"][1]'
            div = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if div:
                style = div.get_attribute("style")
                match = re.search(r"background-image: url\(&quot;(.*)&quot;\)", style)
                if match:
                    update_img(video, match.group(1), filename)
                    return True

        elif site == "spankbang":
            image_xpath = '//*[@class="play_cover"]/img[1]'
            img = driver.xpath(image_xpath)
            if img:
                update_img(video, img[0].get("src"), filename)
                return True

    except Exception:
        print(f"Error getting image for {video}")
        traceback.print_exc()
    return False


def validateVideo(video):
    site = video['site']
    url = getUrl(site, video['id'])

    if (site == 'pornhub'):
        xpath = "//div[@id='player']//video"
    else:
        xpath = "//video"

    tries = 0
    previousValid = video.get('valid', True)
    valid = None
    time.sleep(1)
    while tries < 3 and valid is None:
        try:
            try:
                if site == 'spankbang':
                    content = scraper.get(url).text
                    soup = Soup(content, "lxml")
                    dom = etree.HTML(str(soup))
                    if dom.xpath(xpath_invalid_spankbang):
                        valid = False
                    else:
                        valid = get_image(dom, site, video)
                else:
                    driver.get(url)
                    driver.execute_script(
                        'videos = document.querySelectorAll("video"); for(video of videos) {video.pause()};')
                    valid = get_image(driver, site, video)


                # print(f"{url} is valid: {valid}")

            except:
                valid = False
                # print(f"{url} is valid: {valid}")
                traceback.print_exc()
        except KeyboardInterrupt:
            sys.exit()
        except:
            tries += 1
            traceback.print_exc()
        finally:
            pass

    if valid is not None:
        video['valid'] = valid
        if not previousValid and not valid:
            video['ignore'] = True
        video['last_checked'] = datetime.utcnow()


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()


class CustomDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.try_datetime, *args, **kwargs)

    @staticmethod
    def try_datetime(d):
        ret = {}
        for key, value in d.items():
            try:
                ret[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                ret[key] = value
        return ret


def looptopics(sourceIndexFile, topics, funscriptsFolder):
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
                    newvideos = parsePage(formatHTML(getPage(topic['url'])), topic, funscriptsFolder)
                    if (newvideos and len(newvideos) > 0):
                        for video in newvideos:
                            if (video):
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


def readTopicList():
    all = readInfiniscroll('latest',
                           'https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/latest.json?ascending=false',
                           pages)
    jsonStr = json.dumps(all, indent=4)
    with open('topics.json', "w") as outfile:
        outfile.write(jsonStr)


sourceIndexFile = 'index-source.json'
indexFile = 'index.json'
modelVersion = 1

seleniumLogin()
# savePage("page.html", 'https://discuss.eroscripts.com/t/cock-hero-dreamscape-5-blissful-immersion/49864')

upgradeScript(sourceIndexFile, modelVersion)

pages = 20
readTopicList()
f = open('topics.json')
all = json.load(f)
funscriptsFolder = 'funscripts'
videosAdded = looptopics(sourceIndexFile, all, funscriptsFolder)
print('Added ' + str(videosAdded) + ' videos.')

saveIndex(sourceIndexFile, indexFile)
validateSelenium(sourceIndexFile)
saveIndex(sourceIndexFile, indexFile)

# Close.
driver.close()
# display.stop()
