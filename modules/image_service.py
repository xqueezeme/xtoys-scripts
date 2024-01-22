import base64
import os
import re
import traceback
import unicodedata
from io import BytesIO

import cloudscraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance
import requests
from PIL import Image

image_folder = 'images'

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


def update_img(video, data_url, filename):
    if data_url:
        if not os.path.exists(image_folder + '/' + filename):
            video['thumbnail'] = 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + image_folder + '/' + filename
            print(f"Updating thumbnail {video['name']}")

            with open(image_folder + "/" + filename, "w") as outfile:
                outfile.write(data_url)
        else:
            video['thumbnail'] = 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + image_folder + '/' + filename
def create_image(image_link):
    if image_link:
        data_url = create_image_data_url(image_link)
        return data_url


def get_image(driver, site, video, dom=None):
    try:
        if site == "eporner":
            image_xpath = "//*[@id='moviexxx']/div[@poster]"
            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:

                image = create_image(img.get_attribute("poster"))
                return image

        elif site == "pornhub":
            image_xpath = '//*[@id="player"]//img'
            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:
                image = create_image(img.get_attribute("src"))

                return image

        elif site == "xvideos":
            image_xpath = '//*[@class="video-pic"]/img'
            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:
                image = create_image(img.get_attribute("src"))
                return image

        elif site == "xhamster":
            image_xpath = '//*[contains(@class,"xplayer-fallback-image")][1]'
            div = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if div:
                style = div.get_attribute("style")
                if style:
                    match = re.search(r"background-image: url\(\"(.*)\"\)", style)
                    if match:
                        image = create_image(match.group(1))
                        return image

        elif site == "spankbang":
            if dom is not None:
                image_xpath = '//*[@class="play_cover"]/img[1]'
                img = dom.xpath(image_xpath)
                if img:
                    image = create_image(img[0].get("src"))
                    return image

    except Exception:
        print(f"Error getting image for {video}")
        traceback.print_exc()
    return None

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
