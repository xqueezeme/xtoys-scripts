
from http import cookies
from multiprocessing import allow_connection_pickling
from bs4 import BeautifulSoup as Soup

import re
from urllib.request import build_opener, HTTPCookieProcessor, Request
import os
import requests
from pathlib import Path
import yaml
from yaml.loader import SafeLoader
from fake_useragent import UserAgent
import time
import numpy as np
import requests
from hyper.contrib import HTTP20Adapter
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import lxml.etree as etree
import lxml.html as LH
from pathlib import Path
import uuid
import json

username = 'excusemi'
password = 'ZATU5KDs8tifnF'
ua = UserAgent()
userAgent = str(ua.chrome)
session = requests.Session()
f = open('./credentials.json')
credentials = json.load(f)
def getPage(url):
    response = session.get(url)
    print(response)
    return response.text

def seleniumLogin():
    driver = webdriver.Chrome()
    driver.get('https://discuss.eroscripts.com/login')
    driver.implicitly_wait(10)
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
    time.sleep(3)
    cookies = {}
    selenium_cookies = driver.get_cookies()
    for cookie in selenium_cookies:
        cookies[cookie['name']] = cookie['value']
    session.cookies.update(cookies)

    # Close.
    driver.close()
#login()
    
seleniumLogin()
def download_file(filename, url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with session.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

def getSpankbangId(url):
    print(url)

    regex = re.compile(r'pankbang.com\/(.*)\/video')
    return regex.search(url)[1]
def getPornhubId(url):
    print(url)
    regex = re.compile(r'viewkey=([a-z0-9]+)')
    return regex.search(url)[1]
def parsePage(text, topic):
    soup = Soup(text, "lxml")
    dom = etree.HTML(str(soup))
    firstPost = dom.xpath("//div[contains(@class, 'contents')]")[0]
    spankbang = None
    pornhub = None
    spankbangSel = dom.xpath('//a[contains(@href,"spankbang.com")]/@href')
    if(len(spankbangSel) == 1 and not str(spankbangSel[0]).__contains__('/playlist/')):
        spankbang = spankbangSel[0]
    pornhubSel = dom.xpath('//a[contains(@href,"pornhub.com")]/@href')
    if(len(pornhubSel) == 1 and not str(pornhubSel[0]).__contains__('pornhub.com/pornstar/')):
        pornhub = pornhubSel[0]
    funscripts = []
    regexpNS = 'http://exslt.org/regular-expressions'
    links = dom.xpath("//a[re:test(@href, '(\.funscript$)')]", namespaces={'re':regexpNS})

    for link in links:
        funscripts.append('https://discuss.eroscripts.com' + link.get("href"))
    if((spankbang or pornhub) and len(links) > 0):
        if(spankbang):
            id = getSpankbangId(spankbang)
            site = 'spankbang'
        elif(pornhub):
            id = getPornhubId(pornhub)
            site = 'pornhub'

        download_file('../funscripts/' + topic['slug'] +'.funscript',funscripts[0])
        video = { 
            "name": topic['title'],
            "site": site,
            "id": id,
            "script": 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/funscripts/' + topic['slug']+'.funscript',
            "tags": topic['tags'],
            "url": topic['url'],
            "created_at": topic['created_at']
        }
        return video
    return None
    #print(etree.tostring(dom))
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


def readInfiniscroll(url, pages):
    newTopics = []
    for i in range(0,pages):
        print('scroll index : ' + str(i))
        scrollJson = getPage(url + str(i))
        #print(scrollJson)
        data = json.loads(scrollJson)
        topics = data['topic_list']['topics']
        for topic in topics:
            newTopics.append({ 'url': 'https://discuss.eroscripts.com/t/dicks/'+str(topic['id']),
                               'title': topic['title'],
                               'slug': topic['slug'],
                               'created_at': topic['created_at'],
                               'tags': topic['tags']})
    return newTopics



def looptopics(indexFile, topics):
    f = open(indexFile)
    data = json.load(f)

    videos = data['videos']
    print('topics: ' + str(len(topics)))
    filteredTopics = filter(lambda topic: next(filter(lambda video: video['name'] == topic['title'], videos), None) == None, topics)
    for topic in filteredTopics:
        print(json.dumps(topic))
        video = parsePage(formatHTML(getPage(topic['url'])), topic)
        if(video):
            existingVideo = next(filter(lambda existing: existing['id'] == video['id'] and existing['site'] == video['site'], videos), None)
            if(existingVideo == None):
                videos.append(video)
            else:
                existingVideo['tags'] = video['tags']
                jsonStr = json.dumps(data, indent=4)
                print('Writing json')
                with open(indexFile, "w") as outfile:
                    outfile.write(jsonStr)
#topTopics = readInfiniscroll('https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/top.json?ascending=false&per_page=50&period=all&page',100)
#lastestopics = readInfiniscroll('https://discuss.eroscripts.com/c/scripts/free-scripts/14/l/latest.json?ascending=false&per_page=50&&page=',100)
#topics = np.concatenate((lastestopics, topTopics))
#looptopics('../index-test.json', topics)

video = parsePage(formatHTML(getPage('https://discuss.eroscripts.com/t/dicks/39219')),None)
#video = parsePage(formatHTML(getPage('https://discuss.eroscripts.com/t/mythriljay-mega-pack-6-more-music-10-pmvs/27519')), None)
