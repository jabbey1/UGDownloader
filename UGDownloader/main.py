import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Firefox()  # create instance of browser

# get artist text input here
# TODO: build out gui here, get artist, username, password
artist = 'Wormrot'  # case-sensitive match
# navigate to site, go to artist page, then filter out text tabs
driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
driver.find_element(By.LINK_TEXT, artist).click()
driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
# Login required...
driver.find_element(By.CSS_SELECTOR, '.exTWY > span:nth-child(1)').click()  # login button
usernameTextbox = driver.find_element(By.CSS_SELECTOR, '.wzvZg > div:nth-child(1) > input:nth-child(1)')
passwordTextbox = driver.find_element(By.CSS_SELECTOR, '.wlfii > div:nth-child(1) > input:nth-child(1)')
usernameTextbox.send_keys('jake.c.abbey')
passwordTextbox.send_keys('!bRD3*@erWRZ54')
passwordTextbox.send_keys(Keys.RETURN)
print('logged in hopefully')
# todo if found element of the login area still around, then login failed
# todo is below the popup?
driver.find_element(By.CSS_SELECTOR, 'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)').click()
# create list of elements on page, referring to all the tabs by an artist. skip ones that are pro or official

# todo put the downloading functionality in it's own class
tabList = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
tabList[:] = [x for x in tabList if x.text.__contains__('Guitar Pro')]
howManyTabs = len(tabList)
print('Found ' + str(len(tabList)) + ' Guitar Pro Files')

# download for each element, skipping pro or official
for i in range(howManyTabs):
    tabList = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
    tabList[:] = [x for x in tabList if x.text.__contains__('Guitar Pro')]
    print(tabList[i].find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href')) # print link
    tabList[i].find_element(By.CSS_SELECTOR, '.HT3w5').click()
    button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
    time.sleep(.1)
    driver.execute_script("window.stop();")  # stop their player from loading
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
    time.sleep(.1)
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
    time.sleep(.1)
    # click download button, go back
    # todo comment below line out for testing
    # button.click()  # TODO: why is there a huge delay after this?
    driver.back()

# todo go to next page and repeat

driver.close()