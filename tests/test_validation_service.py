from unittest import TestCase

from selenium import webdriver

from modules import validation_service
import chromedriver_binary_sync


# Download chromedriver to current directory.
# (chromedriver version matches installed chrome)


class Test(TestCase):
    def test_validate_video(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        video = {
            "name": "Lily Kawaii - POV Asian Blowjob",
            "site": "eporner",
            "id": "YxulHyEGKVv",
            "scripts": [
                {
                    "name": "Lily Kawaii - POV Asian Blowjob.funscript",
                    "location": "https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/funscripts/lily-kawaii-pov-asian-blowjob-1.funscript"
                }
            ],
            "tags": [
                "blowjob",
                "pov",
                "asian",
                "action",
                "facial"
            ],
            "created_at": "2024-01-20T05:54:59.378Z",
            "url": "https://discuss.eroscripts.com/t/lily-kawaii-pov-asian-blowjob/142542",
            "valid": False,
            "creator": "TheFunscripter",
            "ignore": False,
            "last_checked": "2024-01-20T22:55:02.964229",
            "thumbnail": "https://raw.githubusercontent.com/xqueezeme/xtoys-scripts/main/images/lily-kawaii-pov-asian-blowjob.jpeg"
        }
        validation_service.validateVideo(driver,
                                         video
                                         )
        self.assertTrue(video.get('valid'))
        sourceIndexFile = 'index-source.json'
        validation_service.validate_selenium(driver, sourceIndexFile, "eporner")
    def test_validate_videos_eporner(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        sourceIndexFile = '../index-source.json'
        validation_service.validate_selenium(driver, sourceIndexFile, "eporner")
    def test_validate_videos_spankbang(self):
        chromedriver_binary_sync.download()

        driver = webdriver.Chrome()
        sourceIndexFile = '../index-source.json'
        validation_service.validate_selenium(driver, sourceIndexFile, "spankbang")
