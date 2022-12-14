import os
import time
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def get_tabs(driver):
    tab_list = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
    tab_links = []
    tab_list[:] = [x for x in tab_list if x.text.__contains__('Guitar Pro')]
    for i in tab_list:
        tab_links.append(i.find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))
    how_many_tabs = len(tab_list)
    print('Found ' + str(how_many_tabs) + ' Guitar Pro Files')
    # download for each element, skipping pro or official
    download_count = 0
    failure_count = 0
    for i in range(how_many_tabs):
        tries = 1
        while True:  # used to restart iterations of for loop
            tries += 1
            if tries > 9:  # Count # of tries for current file, to prevent getting stuck
                print('Too many download attempts, moving on.')
                failurelog = open('failurelog.txt', 'a')
                failurelog.write(tab_links[i])
                failurelog.write('\n')
                failurelog.close()
                break
            print(tab_links[i])
            driver.get(str(tab_links[i]))

            scroll_to_bottom(driver)
            try:
                button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
            except Exception as e:  # sometimes the button is obscured by other elements
                print(e)
                print('Button obscured? trying again.') # I don't think this error is ever hitting
                failure_count += 1
                continue
            try:
                if driver.which_browser == 'Chrome':
                    driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(EC.element_to_be_clickable(button)))
                if driver.which_browser == 'Firefox':
                    driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20).until(EC.element_to_be_clickable(button)))
                    time.sleep(.6)  # think this can go down to .5 at least todo optimize
                download_count += 1
                tries = 0
                break
            except (TypeError, selenium.common.exceptions.ElementNotInteractableException):
                print('ElementNotInteractableException, retrying page.')
                print("Try number: " + str(tries))
                failure_count += 1
            except Exception as e:
                print(e.args[0])
                print('Something went wrong, retrying page')
                print("Try number: " + str(tries))
                failure_count += 1
    return [download_count, failure_count]


def create_artist_folder(dl_path):
    try:
        os.mkdir(dl_path)
    except OSError as error:
        print(error)
    else:
        print("Folder created at " + dl_path)


def scroll_to_bottom(driver):
    # todo check if times can be cut/shortened
    time.sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
    time.sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
    time.sleep(.1)
