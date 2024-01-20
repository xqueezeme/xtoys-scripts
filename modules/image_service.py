import base64
import os
import re
import traceback
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


def update_img(video, image_link, filename):
    if image_link:
        if not os.path.exists(image_folder + '/' + filename):
            data_url = create_image_data_url(image_link)
            if data_url:
                video[
                    'thumbnail'] = 'https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/' + image_folder + '/' + filename
                print(f"Updating thumbnail {video['name']}")

                with open(image_folder + "/" + filename, "w") as outfile:
                    outfile.write(data_url)


def get_image(driver, site, video):
    filename = slugify(video['name']) + '.jpeg'
    try:
        if site == "eporner":
            image_xpath = "//*[@id='moviexxx']/div[@poster]"
            img = WebDriverWait(driver, 1).until(
                EC.presence_of_element_located((By.XPATH, image_xpath))
            )
            if img:
                update_img(video, img.get_attribute("poster"), filename)

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
