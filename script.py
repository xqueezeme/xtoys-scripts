
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

xpath_invalid_spankbang = "//*[contains(text(),'deze video is niet langer beschikbaar.')]"
xpath_invalid_pornhub = "//*[contains(text(), 'Fout Pagina Niet Gevonden')]"

ua = UserAgent()
userAgent = str(ua.chrome)
session = requests.Session()
f = open('./credentials.json')
credentials = json.load(f)
options = webdriver.FirefoxOptions()
options.add_argument("--mute-audio")
options.add_argument('--disable-browser-side-navigation')

options.add_argument("--headless")
driver = webdriver.Firefox(options=options)

def getPage(url):
    try:
        response = session.get(url)
        return response.text
    except:
        print('Error trying to access ' + url+'\nTrying again in 10 sec')
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



def download_file(filename, url):
    local_filename = url.split('/')[-1]        
    # NOTE the stream=True parameter below
    try:
        with session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        return local_filename
    except:
        print('Error trying to download ' + url+'\nTrying again in 10 sec')
        time.sleep(5)
        return download_file(filename, url)


def getSpankbangId(url):
    regex = re.compile(r'spankbang.com\/([a-z0-9]+)\/video')
    return regex.search(url)[1]
def getPornhubId(url):
    regex = re.compile(r'viewkey=([a-z0-9]+)')
    return regex.search(url)[1]
def getXvideosId(url):
    regex = re.compile(r'\/video(\d+)\/')
    return regex.search(url)[1]
def getXhamsterId(url):
    regex = re.compile(r'xhamster\.com\/videos\/(.*)\/?.*')
    group =  regex.search(url)[1]
    split = group.split('-')
    return split[len(split)-1]
def getUrl(site, id):
    if(site == 'pornhub'):
        return 'https://nl.pornhub.com/view_video.php?viewkey=' + id
    elif(site == 'spankbang'):
        return 'https://nl.spankbang.com/' + id + '/video/test'
    elif(site == 'xvideos'):
        return 'https://www.xvideos.com/video' + id + '/xxx'
    elif(site == 'xhamster'):
        return 'https://nl.xhamster.com/videos/xxx-' + id
    return None

def testVideoPornhub(id):
    response = session.get('https://nl.pornhub.com/view_video.php?viewkey=' + id)
    ok = response.status_code != 404 and not response.text.__contains__('Page Not Found')
    title = ''
    return { "ok": ok, "title": title}

def testVideoSpankbang(id):
    response = session.get('https://nl.spankbang.com/' + id + '/video/test')
    ok = response.status_code != 404
    title = ''
    return { "ok": ok, "title": title}
def testVideoXhamster(id):
    response = session.get('https://nl.xhamster.com/videos/xxx-' + id)
    ok = response.status_code != 404
    title = ''
    return { "ok": ok, "title": title}
def testVideoXvideo(id):
    response = session.get('https://www.xvideos.com/video' + id + '/xxx')
    ok = response.status_code != 404
    title = ''
    return { "ok": ok, "title": title}
def findPornhubIds(pornhubSel):
    links = []
    if(len(pornhubSel)>0):
        for a in pornhubSel:
            if(not str(a).__contains__('pornhub.com/pornstar/') and not str(a).__contains__('pornhub.com/model/') and not str(a).__contains__('pornhub.com/users/') and not str(a).__contains__('pornhub.com/playlist/') and not str(a).__contains__('pornhub.com/channels/')):
                try:
                    id = getPornhubId(str(a))
                    if(id):
                        valid =testVideoPornhub(id)
                        if(valid and valid['ok']):
                            links.append(id)
                except:
                    print('failed on ' + str(a))
    return list(set(links))
def findSpankbangIds(spankbangSel):
    links = []
    if(len(spankbangSel)>0):
        for a in spankbangSel:
            if(not str(a).__contains__('/playlist/') and not str(a).__contains__('/profile/')):
                try:
                    id = getSpankbangId(str(a))
                    if(id):
                        valid =testVideoSpankbang(id)
                        if(valid and valid['ok']):
                            links.append(id)
                except:
                    print('failed on ' + str(a))
    return list(set(links))
def findXvideosIds(xvideosSel):
    links = []
    if(len(xvideosSel)>0):
        for a in xvideosSel:
            if(not str(a).__contains__('/profile/')):
                try:
                    id = getXvideosId(str(a))
                    if(id):
                        valid =testVideoXvideo(id)
                        if(valid and valid['ok']):
                            links.append(id)
                        else:
                            print(str(a) + ' is invalid')
                    else:
                        print('Could not create id for ' + str(a))
                except:
                    print('failed on ' + str(a))
    return list(set(links))
def findXhamsterIds(xhamsterSel):
    links = []
    if(len(xhamsterSel)>0):
        for a in xhamsterSel:
            try:
                id = getXhamsterId(str(a))
                if(id):
                    valid =testVideoXhamster(id)
                    if(valid and valid['ok']):
                        links.append(id)
            except:
                print('failed on ' + str(a))
    return list(set(links))

def parsePost(post,topic):
    spankbang = None
    pornhub = None
    xvideos = None
    xhamster = None

    spankbangSel = post.xpath('.//a[contains(@href,"spankbang.com")]/@href')

    spankbangLinks = findSpankbangIds(spankbangSel)
    if(len(spankbangLinks) ==  1):
        spankbang = spankbangLinks[0]

    pornhubSel = post.xpath('.//a[contains(@href,"pornhub.com")]/@href')
    pornhubLinks = findPornhubIds(pornhubSel)
    if(len(pornhubLinks) == 1): 
        pornhub = pornhubLinks[0]

    xvideosSel = post.xpath('.//a[contains(@href,"xvideos.com")]/@href')
    xvideosLinks = findXvideosIds(xvideosSel)
    if(len(xvideosLinks) == 1): 
        xvideos = xvideosLinks[0]

    xhamsterSel = post.xpath('.//a[contains(@href,"xhamster.com")]/@href')
    xhamsterLinks = findXhamsterIds(xhamsterSel)
    if(len(xhamsterLinks) == 1): 
        xhamster = xhamsterLinks[0]

    funscripts = []
    regexpNS = 'http://exslt.org/regular-expressions'
    links = post.xpath(".//a[re:test(@href, '(\.funscript$)')]", namespaces={'re':regexpNS})

    for link in links:
        if(link.get("href").startswith('http')):
            funscripts.append(link.get("href"))
        else:
            funscripts.append('https://discuss.eroscripts.com' + link.get("href"))
    if((spankbang or pornhub or xvideos or xhamster) and len(links) > 0):
        if(spankbang):
            id = spankbang
            site = 'spankbang'
        elif(pornhub):
            id = pornhub
            site = 'pornhub'
        elif(xvideos):
            id =  xvideos
            site = 'xvideos'
        elif(xhamster):
            id = xhamster
            site = 'xhamster'
        if(id):
            filename = topic['slug'] + '.funscript'
            download_file('funscripts/' + filename, funscripts[0])
            video = {
                "name": topic['title'],
                "site": site,
                "id": id,
                "script": 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/funscripts/' + filename,
                "tags": topic['tags'],
                "created_at": topic['created_at'],
                "url": topic['url'],
                "valid": True,
                "creator": topic['username']
            }
            return video
        else:
            print('Video is invalid ' + site + ' id: ' + id)
        return None

def parsePage(text, topic):
    soup = Soup(text, "lxml")
    dom = etree.HTML(str(soup))
    posts = dom.xpath('//div[contains(@itemprop,"articleBody")]')
    videos = []
    if(len(posts) > 0):
        video = parsePost(posts[0], topic)
        if(video):
            videos.append(video)
    return videos
    
def formatHTML(content):
    start = content.index('<body')
    end = content.index('</body>')
    return '<!DOCTYPE html><html lang="en">' + content[start: end-1] + '</body></html'

def parseCategoryPage(text):
    soup = Soup(text, "lxml")
    dom = etree.HTML(str(soup))
    topicLinks= dom.xpath('//a[contains(@href,"/t/")]')
    topics = []
    if(len(topicLinks) > 0):
        for topicLink in topicLinks:
            topics.append({ 'url': topicLink.get("href"),
                                'title':''.join(topicLink.itertext())})
    return topics


def readInfiniscroll(by, url, pages):
    newTopics = []
    for i in tqdm (range(pages), 
               desc="Reading " + by + " topics", 
               ascii=False, ncols=75):
        scrollJson = getPage(url + str(i))
        #print(scrollJson)
        data = json.loads(scrollJson)
        if(data):
            topicsUsers = data.get('users')
            topicList = data.get('topic_list')
            topics = topicList.get('topics')
            ['topics']
            if len(topics) >0:
                for topic in topics:
                    username =''
                    if(topicsUsers):
                        originalPoster = next(filter(lambda poster: poster.get('description') == 'Original Poster', topic.get('posters')),None)
                        if(originalPoster):
                            user = next(filter(lambda user: user.get('id') == originalPoster.get('user_id'), topicsUsers), None)
                            if(user):
                                username = user.get('username')

                    newTopics.append({ 'url': 'https://discuss.eroscripts.com/t/xxx/'+str(topic.get('id')),
                                    'title': topic.get('title'),
                                    'slug': topic.get('slug'),
                                    'created_at': topic.get('created_at'),
                                    'tags': topic.get('tags'),
                                    'username': username
                                    })
            else:
                break
        else:
            break
    return newTopics

def validateJson(indexFile):
    f = open(indexFile)
    data = json.load(f)
    videos = data['videos']
    for idx in tqdm (range(len(videos)), 
               desc="Validating existing videos", 
               ascii=False, ncols=75):
        video = videos[idx]
        if(video['valid'] == True):
            valid = None
            tries = 0
            while tries < 5 and valid == None:
                try:
                    if(video['site'] == 'pornhub'):
                        valid = testVideoPornhub(video['id'])
                    elif(video['site'] == 'spankbang'):
                        valid = testVideoSpankbang(video['id'])
                    elif(video['site'] == 'xhamster'):
                        valid = testVideoXhamster(video['id'])
                    elif(video['site'] == 'xvideos'):
                        valid = testVideoXvideo(video['id'])
                except:
                    tries+=1
                    time.sleep(5)
            
            if(not valid == None and valid['ok'] == True):
                video['valid'] = True
            else:
                video['valid'] = False
        time.sleep(10)

    data['videos'] = videos
    jsonStr = json.dumps(data, indent=4)
    with open(indexFile, "w") as outfile:
        outfile.write(jsonStr)

def validateSelenium(indexFile):
    f = open(indexFile)
    data = json.load(f)
    videos = data['videos']
    for idx in tqdm (range(len(videos)), 
               desc="Validating existing videos", 
               ascii=False, ncols=75):
        video = videos[idx]
        valid = None
        site = video['site']
        url = getUrl(site, video['id'])
        xpath = "//video"
        if (site == 'pornhub'):
            xpath = "//div[@id='player']//video"
        try:
            driver.get(url)
            driver.execute_script('videos = document.querySelectorAll("video"); for(video of videos) {video.pause()}')
            try:
                input = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                valid = True
                print(url + ' is valid')

            except: 
                valid = False
                print(url + ' is invalid')
            video['valid'] = valid
        except:
            traceback.print_exc()


    data['videos'] = videos
    jsonStr = json.dumps(data, indent=4)
    with open(indexFile, "w") as outfile:
        outfile.write(jsonStr)

def looptopics(indexFile, topics):
    f = open(indexFile)
    data = json.load(f)
    videos = data['videos']

    for idx in tqdm (range (len(topics)), 
               desc="Getting videos from topics", 
               ascii=False, ncols=75):
        topic = topics[idx]
        matchingVideo = next(filter(lambda existing: existing['name'] == topic['title'], videos), None)
        if(matchingVideo):
            matchingVideo['tags'] = topic['tags']
            matchingVideo['creator'] = topic['username']
            matchingVideo['created_at'] = topic['created_at']

        else:
            newvideos = parsePage(formatHTML(getPage(topic['url'])), topic)
            if (newvideos):
                for video in newvideos:
                    if(video):
                        existingVideo = next(filter(lambda existing: existing['id'] == video['id'] and existing['site'] == video['site'], videos), None)
                        if(existingVideo == None):
                            videos.append(video)
                        else:
                            existingVideo['tags'] = video['tags']
                            existingVideo['creator'] = video['creator']
                            existingVideo['created_at'] = video['created_at']
        data['videos'] = videos
        jsonStr = json.dumps(data, indent=4)
        with open(indexFile, "w") as outfile:
            outfile.write(jsonStr)

jsonFile = 'index.json'




seleniumLogin()

pages = 100
all = readInfiniscroll('top', 'https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/top.json?ascending=false&per_page=50&period=all&page=',60)
lastestopics = readInfiniscroll('latest', 'https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/latest.json?ascending=false&per_page=50&&page=',pages)
for topic in lastestopics:
    all.append(topic)
looptopics(jsonFile, all)
validateSelenium(jsonFile)
# Close.
driver.close()