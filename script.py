
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

def findPornhubIds(pornhubSel):
    links = []
    if(len(pornhubSel)>0):
        for a in pornhubSel:
            if(not str(a).__contains__('pornhub.com/pornstar/') and not str(a).__contains__('pornhub.com/model/') and not str(a).__contains__('pornhub.com/users/') and not str(a).__contains__('pornhub.com/playlist/') and not str(a).__contains__('pornhub.com/channels/')):
                try:
                    id = getPornhubId(str(a))
                    if(id):
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
                        links.append(id)
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
                    links.append(id)
            except:
                print('failed on ' + str(a))
    return list(set(links))
def parsePost(post,topic,funscriptsFolder):
    spankbang = None
    pornhub = None
    xvideos = None
    xhamster = None

    spankbangSel = post.xpath('.//*[not(blockquote)]//a[contains(@href,"spankbang.com")]/@href')

    spankbangLinks = findSpankbangIds(spankbangSel)
    if(len(spankbangLinks) ==  1):
        spankbang = spankbangLinks[0]

    pornhubSel = post.xpath('.//*[not(blockquote)]//a[contains(@href,"pornhub.com")]/@href')
    pornhubLinks = findPornhubIds(pornhubSel)
    if(len(pornhubLinks) == 1): 
        pornhub = pornhubLinks[0]

    xvideosSel = post.xpath('.//*[not(blockquote)]//a[contains(@href,"xvideos.com")]/@href')
    xvideosLinks = findXvideosIds(xvideosSel)
    if(len(xvideosLinks) == 1): 
        xvideos = xvideosLinks[0]

    xhamsterSel = post.xpath('.//*[not(blockquote)]//a[contains(@href,"xhamster.com")]/@href')
    xhamsterLinks = findXhamsterIds(xhamsterSel)
    if(len(xhamsterLinks) == 1): 
        xhamster = xhamsterLinks[0]
    videosCount = len(pornhubLinks) + len(xvideosLinks) + len(spankbangLinks) + len(xhamsterLinks)
    funscripts = []
    regexpNS = 'http://exslt.org/regular-expressions'
    links = post.xpath(".//*[not(blockquote)]//a[re:test(@href, '(\.funscript$)')]", namespaces={'re':regexpNS})

    for link in links:
        if(link.get("href").startswith('http')):
            funscripts.append({'location' : link.get("href"), 'name': ''.join(link.itertext())})
        else:
            funscripts.append({'location' : 'https://discuss.eroscripts.com' + link.get("href"), 'name': ''.join(link.itertext())})

    if(videosCount ==1 and len(funscripts) > 0 and len(funscripts) <= 3):
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
            funscriptIndex = 1
            scripts = []
            for funscript in funscripts:
                filename = topic['slug'] + '-' + str(funscriptIndex) + '.funscript'
                download_file(funscriptsFolder + '/' + filename, funscript['location'])
                scripts.append({'name': funscript['name'], 'location': 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + funscriptsFolder + '/' + filename})
                funscriptIndex += 1
            video = {
                "name": topic['title'],
                "site": site,
                "id": id,
                "scripts": scripts,
                "tags": topic['tags'],
                "created_at": topic['created_at'],
                "url": topic['url'],
                "valid": True,
                "creator": topic['username'],
                "ignore" : False
            }
            return video
        else:
            print('Video is invalid ' + site + ' id: ' + id)
        return None

def parsePage(text, topic, funscriptsFolder):
    soup = Soup(text, "lxml")
    dom = etree.HTML(str(soup))
    posts = dom.xpath('//div[contains(@itemprop,"articleBody")]')
    videos = []
    if(len(posts) > 0):
        video = parsePost(posts[0], topic, funscriptsFolder)
        if(video):
            videos.append(video)
    return videos
    
def formatHTML(content):
    start = content.index('<body')
    end = content.index('</body>')
    return '<!DOCTYPE html><html lang="en">' + content[start: end-1] + '</body></html'


titleEscapeWords = [ 'mega', 'compilation', 'pack']
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
            if len(topics) >0:
                for topic in topics:
                    username =''
                    if(topicsUsers):
                        originalPoster = next(filter(lambda poster: poster.get('description').__contains__('Original Poster'), topic.get('posters')),None)
                        if(originalPoster):
                            user = next(filter(lambda user: user.get('id') == originalPoster.get('user_id'), topicsUsers), None)
                            if(user):
                                username = user.get('username')
                    title = topic.get('title', None)
                    if title:
                        if(next(filter(lambda keyword: title.lower().__contains__(keyword), titleEscapeWords), None) != None):
                            newTopics.append({ 'url': 'https://discuss.eroscripts.com/t/xxx/'+str(topic.get('id')),
                                            'title': title,
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

def upgradeScript(indexFile, modelVersion):
    f = open(indexFile)
    data = json.load(f)
    data['version'] = modelVersion
    videos = data['videos']
    for idx in tqdm (range(len(videos)), 
               desc="Upgrading script videos", 
               ascii=False, ncols=75):
        video = videos[idx]
        if(video.get('ignore', False) == False):
            scripts = []
            if(video.get('script', None) != None):
                scripts.append({"name" : '', "location": video['script']})
                video['scripts'] = scripts
                video.pop('script', None)
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
                #print(url + ' is valid')

            except: 
                valid = False
                #print(url + ' is invalid')
            video['valid'] = valid
        except:
            traceback.print_exc()


    data['videos'] = videos
    jsonStr = json.dumps(data, indent=4)
    with open(indexFile, "w") as outfile:
        outfile.write(jsonStr)

def looptopics(indexFile, topics, funscriptsFolder):
    f = open(indexFile)
    data = json.load(f)
    videos = data['videos']
    videosAdded = 0
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
            newvideos = parsePage(formatHTML(getPage(topic['url'])), topic, funscriptsFolder)
            if (newvideos):
                for video in newvideos:
                    if(video):
                        existingVideo = next(filter(lambda existing: existing['id'] == video['id'] and existing['site'] == video['site'], videos), None)
                        if(existingVideo == None):
                            videos.append(video)
                            videosAdded += 1
                        else:
                            existingVideo['tags'] = video['tags']
                            existingVideo['creator'] = video['creator']
                            existingVideo['created_at'] = video['created_at']
        data['videos'] = videos
        jsonStr = json.dumps(data, indent=4)
        with open(indexFile, "w") as outfile:
            outfile.write(jsonStr)

        return videosAdded
def savePage(page, url):
    pageContent = getPage(url)
    with open(page, "w") as outfile:
        outfile.write(pageContent)

def readTopicList():
    all = readInfiniscroll('top', 'https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/top.json?ascending=false&per_page=50&period=all&page=',pages)
    lastestopics = readInfiniscroll('latest', 'https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/latest.json?ascending=false&per_page=50&&page=',pages)
    for topic in lastestopics:
        all.append(topic)

    jsonStr = json.dumps(all, indent=4)
    with open('topics.json', "w") as outfile:
        outfile.write(jsonStr)
seleniumLogin()

jsonFile = 'index.json'
modelVersion = 1
upgradeScript(jsonFile, modelVersion)

pages = 50

readTopicList()
f = open('topics.json')
all = json.load(f)
funscriptsFolder = 'funscripts'
videosAdded = looptopics(jsonFile, all, funscriptsFolder)
print('Added ' + str(videosAdded) + ' videos.')
validateSelenium(jsonFile)
# Close.
driver.close()
