from modules import validation_service

import os
import re
import time

import lxml.etree as etree
from bs4 import BeautifulSoup as Soup

from modules import validation_service
from modules.constants import FUNSCRIPT_FOLDER


def parse_page_from_url(url, topic, session, driver):
    newvideos = parsePage(
        formatHTML(getPage(session, url)), topic, session, driver)
    return newvideos


def getPage(session, url):
    try:
        response = session.get(url)
        return response.text
    except:
        print('Error trying to access ' + url + '\nTrying again in 10 sec')
        time.sleep(5)
        return getPage(session, url)


def formatHTML(content):
    start = content.index('<body')
    end = content.index('</body>')
    return '<!DOCTYPE html><html lang="en">' + content[start: end - 1] + '</body></html'


def parsePage(text, topic, session, driver):
    soup = Soup(text, "lxml")
    dom = etree.HTML(str(soup))
    posts = dom.xpath('//*[@id="post_1"]/div[@class="post"]')
    videos = []
    if posts:
        post = posts[0]
        if (len(post.xpath('.//hr')) > 0 or len(post.xpath(".//h3[text() =' Details']")) > 1):
            packVideos = parsePack(post)
            for video in packVideos:
                funscriptIndex = 1
                scripts = []
                allscriptsfound = True
                for funscript in video['funscripts']:
                    filename = topic['slug'] + '-' + video['id'] + '-' + str(funscriptIndex) + '.funscript'
                    if (not os.path.exists(FUNSCRIPT_FOLDER + '/' + filename)):
                        file = download_file(session, FUNSCRIPT_FOLDER + '/' + filename, funscript['location'])
                        if (file == None):
                            allscriptsfound = False
                    scripts.append({'name': funscript['name'],
                                    'location': 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + FUNSCRIPT_FOLDER + '/' + filename})
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
                    validation_service.validateVideo(driver, video, append_image=True)
                    videos.append(video)
                else:
                    return None
        else:
            video = parsePost(post, topic, session, driver)
            if video:
                videos.append(video)
    else:
        print("post no found")
    return videos


def parsePost(post, topic, session, driver):
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
        print("Found the correct amount of videos and funscripts")
        id = newVideoLinks[0]
        if (id):
            funscriptIndex = 1
            scripts = []
            allscriptsfound = True
            for funscript in funscripts:
                filename = topic['slug'] + '-' + str(funscriptIndex) + '.funscript'
                if (not os.path.exists(FUNSCRIPT_FOLDER + '/' + filename)):
                    file = download_file(session, FUNSCRIPT_FOLDER + '/' + filename, funscript['location'])
                    if (file == None):
                        allscriptsfound = False
                scripts.append({'name': funscript['name'],
                                'location': 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + FUNSCRIPT_FOLDER + '/' + filename})
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
                validation_service.validateVideo(driver, video)
                return video
            else:
                return None
        return None
    else:
        print("No videos or funscript found!")


def parsePack(post):
    current = ''
    title = None
    link = None
    funscripts = None
    videos = []

    for el in post:
        videoLinks = None

        text = ''.join(el.itertext()).strip().lower()
        if text:
            if current == 'title':
                title = text.split('\n')[0]
                current = None
            elif current == 'link':
                videoLinks = findVideoLinks(el)
                current = None

            elif current == 'script':
                regexpNS = 'http://exslt.org/regular-expressions'
                funscripts = []
                links = el.xpath(".//a[re:test(@href, '(\.funscript$)')]", namespaces={'re': regexpNS})
                if len(links) > 0:
                    for link in links:
                        if (link.get("href").startswith('http')):
                            funscripts.append({'location': link.get("href"), 'name': ''.join(link.itertext())})
                        else:
                            funscripts.append({'location': 'https://discuss.eroscripts.com' + link.get("href"),
                                               'name': ''.join(link.itertext())})
                    current = None
                if title and funscripts and videoLinks and len(videoLinks) == 1:
                    video = videoLinks[0]
                    if title.lower() == 'length':
                        title = funscripts[0]['name'].replace('.funscript', '')
                    videos.append({'title': title, 'site': video['site'], 'id': video['id'], 'funscripts': funscripts})
                title = None
                link = None
                funscripts = None
                videoLinks = None


            elif text == 'details':
                current = 'title'
            elif text == 'video link' or el.get('alt') == ':movie_camera:':
                current = 'link'
            elif text == 'script':
                current = 'script'
        if el.tag == 'hr':
            if title and funscripts and videoLinks and len(videoLinks) == 1:
                video = videoLinks[0]
                if (title.lower() == 'length'):
                    title = funscripts[0]['name'].replace('.funscript', '')
                videos.append({'title': title, 'site': video['site'], 'id': video['id'], 'funscripts': funscripts})
            title = None
            link = None
            funscripts = None
            videoLinks = None
    return videos


epornerAXPath = './/a[contains(@href,"eporner.com")]/@href'
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


def download_file(session, filename, url, retries=0):
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


EPORNER_ID_REGEX1 = re.compile(r'eporner\.com\/video\-([a-zA-Z0-9]+)\/?.*', re.IGNORECASE)
EPORNER_ID_REGEX2 = re.compile(r'eporner\.com\/.*\/([a-zA-Z0-9]+)\/.*', re.IGNORECASE)


def getEpornerId(url):
    group = EPORNER_ID_REGEX1.search(url)
    if (group):
        return group[1]
    return EPORNER_ID_REGEX2.search(url)[1]


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
