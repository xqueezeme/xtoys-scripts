import time
from unittest import TestCase

from selenium import webdriver

from modules import validation_service
import chromedriver_binary_sync


# Download chromedriver to current directory.
# (chromedriver version matches installed chrome)


class Test(TestCase):
    def test_validate_video_eporner(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        video = {
            "name": "Lily Kawaii - POV Asian Blowjob",
            "site": "eporner",
            "id": "YxulHyEGKVv",
            "valid": False
        }
        validation_service.validateVideo(driver,
                                         video
                                         )
        self.assertTrue(video.get('valid'))

    def test_validate_video_spankbang(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        video = {
            "name": "CH Island 5 Episode I",
            "id": "3s6gd",
            "site": "spankbang",
            "valid": False
        }
        validation_service.validateVideo(driver,
                                         video
                                         )
        self.assertTrue(video.get('valid'))

    def test_validate_video_pornhub(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        video = {
            "name": "Eva Elfie - Tries a Big Cock inside her Tight Pussy",
            "site": "pornhub",
            "id": "ph5cdf07d5bbe31",
            "valid": False
        }
        validation_service.validateVideo(driver,
                                         video
                                         )
        self.assertTrue(video.get('valid'))

    def test_validate_video_pornhub_invalid(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        video = {
            "name": "invalid",
            "site": "pornhub",
            "id": "ph5cdf07d5bbe31xxxxx",
            "valid": False
        }
        validation_service.validateVideo(driver,
                                         video
                                         )
        self.assertFalse(video.get('valid'))
    def test_validate_video_xhamster(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()

        video = {
            "name": "Jenna Jameson - POV blowjob",
            "site": "xhamster",
            "id": "xhG64R9",
            "valid": False
        }
        validation_service.validateVideo(driver,
                                         video
                                         )
        self.assertTrue(video.get('valid'))

    def test_validate_videos_eporner(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        sourceIndexFile = '../index-source.json'
        #validation_service.validate_selenium(driver, sourceIndexFile, "eporner")

    def test_validate_videos_spankbang(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        sourceIndexFile = '../index-source.json'
        #validation_service.validate_selenium(driver, sourceIndexFile, "spankbang")


