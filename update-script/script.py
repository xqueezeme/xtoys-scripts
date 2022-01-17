import selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.get("https://scriptaxis.com/script/grind-a-rachel-starr-tribute-pmv")
driver.find_element(By.XPATH, "//a[contains(@href, 'discuss.eroscripts.com') and contains(@class, 'ScriptDetails_source')]").click()


driver.quit()

