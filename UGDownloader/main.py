import selenium
import DLoader
from pathlib import Path
import warnings
import time
import GUI
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC






# get artist text input here
# TODO: build out gui here, get artist, username, password
artist = 'Descendents'  # case-sensitive match

# todo chrome functionality?

# GUI here
gui = GUI.GUI()

# # navigate to site, go to artist page, then filter out text tabs
# driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
# driver.find_element(By.LINK_TEXT, artist).click()
# driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
# # Login required... todo make own method in gui?
# driver.find_element(By.CSS_SELECTOR, '.exTWY > span:nth-child(1)').click()  # login button
# usernameTextbox = driver.find_element(By.CSS_SELECTOR, '.wzvZg > div:nth-child(1) > input:nth-child(1)')
# passwordTextbox = driver.find_element(By.CSS_SELECTOR, '.wlfii > div:nth-child(1) > input:nth-child(1)')
# usernameTextbox.send_keys('jake.c.abbey')
# passwordTextbox.send_keys('!bRD3*@erWRZ54')
# passwordTextbox.send_keys(Keys.RETURN)
# print('logged in hopefully')
# # todo if found element of the login area still around, then login failed
# # Click out of annoying popup
# driver.find_element(By.CSS_SELECTOR, 'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)').click()
# current_page = driver.current_url



print('fin')
