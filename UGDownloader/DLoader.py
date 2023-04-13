import os
import time
import selenium.common.exceptions
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def download_tab(driver, link) -> list[int, int]:
    download_count, failure_count = 0, 0
    driver.get(link)
    print(f'Downloading tab @ {link}')
    try:
        scroll_to_bottom(driver)
        button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
        # button = driver.find_element(By.CSS_SELECTOR, "form[action='https://tabs.ultimate-guitar.com/tab/download']
        # button") button.click()
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20)
                              .until(ec.element_to_be_clickable(button)))
        # seem to need to give firefox time on page after a download, still necessary?
        if driver.which_browser == 'Firefox':
            time.sleep(.65)
        download_count += 1
    except Exception as e:  # sometimes the button is obscured by other elements
        print(e)
        print('Button obscured?')  # I don't think this error is ever hitting
        failure_count += 1
    time.sleep(0.5)
    return [download_count, failure_count]


def collect_links(driver: webdriver) -> list:
    """ Collects links to guitar pro files only, page by page"""
    tab_links, page = [], 1

    while True:
        print(f"Reading page {page}")
        tabs_from_page = [x for x in driver.find_elements(By.CLASS_NAME, 'LQUZJ') if x.text.__contains__('Guitar Pro')]
        for tab in tabs_from_page:
            tab_links.append(tab.find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))

        if driver.find_elements(By.CLASS_NAME, 'BvSfz'):
            page += 1
            driver.find_element(By.CLASS_NAME, 'BvSfz').click()
            continue
        else:
            break

    print(f'Found {len(tab_links)} Guitar Pro Files')
    return tab_links


def failure_log_failed_attempt(text: str):
    failurelog = open('_UGDownloaderFiles\\failurelog.txt', 'a')
    failurelog.write(text)
    failurelog.write('\n')
    failurelog.close()


def create_artist_folder(artist: str) -> str:
    # Need there to already be a 'Tabs' folder
    dl_path = str(Path.cwd()) + '\\Tabs\\' + artist
    # thanks, sawyersteven
    if os.path.isdir(dl_path):
        print("Using folder at " + dl_path)
        return dl_path
    try:
        os.mkdir(dl_path)
    except OSError as error:
        print(error)
        # not graceful:
        # print('Artist folder already exists')
    else:
        print("Folder created at " + dl_path)
    return dl_path  # return path so GUI can set download directory in browser


def scroll_to_bottom(driver: webdriver):
    # todo check if times can be cut/shortened
    time.sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
    time.sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
    time.sleep(.1)


def get_tabs(driver: webdriver) -> list:
    tab_links = collect_links(driver)
    # download for each element, skipping pro or official
    download_count, failure_count = 0, 0
    for i in range(len(tab_links)):
        tries = 0
        while True:  # used to restart iterations of for loop
            tries += 1
            if tries > 8:  # Count # of tries for current file, to prevent getting stuck
                print('Too many download attempts, moving on.')
                failure_log_failed_attempt(tab_links[i])
                break
            print(tab_links[i])
            driver.get(str(tab_links[i]))

            scroll_to_bottom(driver)
            try:
                button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
            except Exception as e:  # sometimes the button is obscured by other elements
                print(e)
                print('Button obscured? trying again.')  # I don't think this error is ever hitting
                failure_count += 1
                continue
            # Actual download button clicking here
            try:
                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 20)
                                      .until(ec.element_to_be_clickable(button)))
                if driver.which_browser == 'Firefox':
                    time.sleep(.65)  # think this can go down to .5 at least todo optimize
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
    time.sleep(.5)
    return [download_count, failure_count]
