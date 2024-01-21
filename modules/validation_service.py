import json
import sys
import time
import traceback
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as Soup

import cloudscraper
from lxml import etree

from modules import sites_service, image_service
from modules.common import CustomDecoder, CustomEncoder

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
xpath_invalid_spankbang = "//*[contains(text(),'deze video is niet langer beschikbaar.')]"


def validate_selenium(driver, sourceIndexFile, all=False, site=None, update_source=True):
    data = None
    with open(sourceIndexFile) as file:
        data = json.load(file, cls=CustomDecoder)
    if data:
        videos = data['videos']
        if all:
            videos_to_validate = list(videos)
        elif site:
            videos_to_validate = list(filter(lambda v:
                                             v.get('site') == site
                                             , videos))
        else:
            videos_to_validate = list(filter(lambda v:
                                             not v.get('ignore', False) and
                                             (v.get('last_checked') is None or v.get(
                                                 'last_checked') < datetime.utcnow() - timedelta(days=7))
                                             , videos))
        for count, video in enumerate(videos_to_validate):
            print(f"Validating video {count} / {len(videos_to_validate)}")
            if video.get('image-data'):
                del video["image-data"]

            validateVideo(driver, video, append_image=True)
            if update_source:
                data['videos'] = videos

                jsonStr = json.dumps(data, indent=4, cls=CustomEncoder)
                with open(sourceIndexFile, "w") as outfile:
                    outfile.write(jsonStr)


def validateVideo(driver, video, append_image=False):
    site = video['site']
    url = sites_service.getUrl(site, video['id'])

    tries = 0
    previousValid = video.get('valid', True)
    image = None
    time.sleep(1)
    while tries < 1 and image is None:
        try:
            if site == 'spankbang':
                content = scraper.get(url).text
                soup = Soup(content, "lxml")
                dom = etree.HTML(str(soup))
                image = image_service.get_image(dom, site, video, dom=dom)
            else:
                driver.get(url)
                driver.execute_script(
                    'videos = document.querySelectorAll("video"); for(video of videos) {video.pause()};')
                image = image_service.get_image(driver, site, video)
                if not image:
                    tries += 1
        except KeyboardInterrupt:
            sys.exit()

        except:
            image = None
            tries += 1

            # print(f"{url} is valid: {valid}")
            traceback.print_exc()
    valid = image is not None
    if append_image and image and not video.get('thumbnail'):
        filename = image_service.slugify(video['name']) + '.jpeg'
        image_service.update_img(video, image, filename)
    print(f"{url} is {'in' if not valid else ''}valid")
    video['valid'] = valid
    if not previousValid and not valid:
        video['ignore'] = True
    video['last_checked'] = datetime.utcnow()
