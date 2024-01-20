import json
import sys
import time
import traceback
from datetime import datetime, timedelta

import cloudscraper
import lxml.etree as etree
from bs4 import BeautifulSoup as Soup

from modules import sites_service, image_service

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
xpath_invalid_spankbang = "//*[contains(text(),'deze video is niet langer beschikbaar.')]"
def validateSelenium(driver, sourceIndexFile):
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

def validateVideo(driver, video):
    site = video['site']
    url = sites_service.getUrl(site, video['id'])

    tries = 0
    previousValid = video.get('valid', True)
    valid = None
    time.sleep(1)
    while tries < 3 and valid is None:
        try:
            try:
                driver.get(url)
                driver.execute_script(
                    'videos = document.querySelectorAll("video"); for(video of videos) {video.pause()};')
                valid = image_service.get_image(driver, site, video)
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
