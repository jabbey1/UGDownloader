import selenium
import DLoader
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# TODO go through styleguide with my program
driver = webdriver.Firefox()  # create instance of browser

# get artist text input here
# TODO: build out gui here, get artist, username, password
artist = 'Descendents'  # case-sensitive match
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


while True:
    DLoader.get_tabs(driver)
    if driver.find_elements(By.CLASS_NAME, 'BvSfz'):
        print("There's another page")
        driver.find_element(By.CLASS_NAME, 'BvSfz').click()
        continue
    else:
        break

driver.close()

