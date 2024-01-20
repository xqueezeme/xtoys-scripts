from unittest import TestCase

from modules import post_service


class Test(TestCase):
    def test_parse_page(self):
        topic = None
        session = None
        text = None
        driver = None

        with open("page.html", "r") as infile:
            text = infile.read()

        html = post_service.formatHTML(text)
        newvideos = post_service.parsePage(html, topic, session, driver)


    def test_get_eporner_id(self):
        self.assertEquals("YxulHyEGKVv", post_service.getEpornerId('https://www.eporner.com/video-YxulHyEGKVv/pov-blowjob-with-asian-teen/'))