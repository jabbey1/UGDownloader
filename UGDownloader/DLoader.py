from os import path, mkdir
from time import sleep
import selenium.common.exceptions
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


def download_tab(driver: webdriver, url: str) -> list[int, int]:
    """Download the file. Navigates to page, scrolls to the bottom where the download button is, and then clicks. If
    the click fails, or the button isn't there, the fallback method is called. Returns values to keep track of total
    number of downloads and failures"""
    download_count, failure_count = 0, 0
    driver.get(url)
    print(f'Downloading tab @ {url}')
    try:
        scroll_to_bottom(driver)
        button = driver.find_element(By.CSS_SELECTOR,
                                     "form[action='https://tabs.ultimate-guitar.com/tab/download'] button")
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 4)
                              .until(ec.element_to_be_clickable(button)))
        # seem to need to give firefox time on page after a download
        if driver.which_browser == 'Firefox':
            sleep(.65)
        download_count += 1
    except Exception as e:  # sometimes the button is obscured by other elements, or button doesn't exist
        # print(e)
        print('Button obscured? Trying fallback method.')
        download_tab_fallback(driver, url)
        failure_count += 1
    sleep(0.5)
    return [download_count, failure_count]


def download_tab_fallback(driver: webdriver, url: str):
    """ This method opens the download link directly in the browser instead
    of using the Download Tab button. This can be used when the button doesn't
    exist (removed tab) or is otherwise unusable. This method works almost all
    of the time, but occasionally will only load the tab's interactive page
    instead of a download link. This may happen because the tab doesn't
    actually exist on UG's server. So this should not be used as the primary
    download strategy, but only as a fallback.
    """
    if driver.current_url != url:
        driver.get(url)
    sleep(.5)
    uid = url.split('-')[-1]
    js_dl = f"window.open('https://tabs.ultimate-guitar.com/tab/download?id={uid}');"
    driver.execute_script(js_dl)
    sleep(.5)


def link_handler(driver: webdriver, tab_links: list, file_type_wanted: str) -> list:
    """Collect a list of the urls to download from, depending on file type desired, building a list containing all
    links of every requested filetype in tab_links."""
    if file_type_wanted in ('Guitar Pro', 'Both'):
        try:
            driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
            tab_links += collect_links_guitar_pro(driver)
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Guitar Pro tabs for this artist.')
    if file_type_wanted in ('Powertab', 'Both'):
        try:
            driver.find_element(By.LINK_TEXT, 'Power').click()
            tab_links += collect_links_powertab(driver)
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Powertabs for this artist.')
    elif file_type_wanted == 'Text':
        print("Not yet implemented")

    return tab_links


def collect_links_guitar_pro(driver: webdriver) -> list:
    """ Collects links to guitar pro files only, page by page"""
    tab_links, page = [], 1

    while True:
        print(f"Reading page {page}")
        tabs_from_page = [x for x in driver.find_elements(By.CLASS_NAME, 'LQUZJ') if 'Guitar Pro' in x.text]
        for tab in tabs_from_page:
            tab_links.append(tab.find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))

        if not driver.find_elements(By.CLASS_NAME, 'BvSfz'):
            break
        page += 1
        driver.find_element(By.CLASS_NAME, 'BvSfz').click()

    print(f'Found {len(tab_links)} Guitar Pro Files')
    return tab_links


def collect_links_powertab(driver: webdriver) -> list:
    """ Collects links to powertab files only, page by page"""
    tab_links, page = [], 1

    while True:
        print(f"Reading page {page}")
        tabs_from_page = [x for x in driver.find_elements(By.CLASS_NAME, 'LQUZJ') if 'Power' in x.text]
        for tab in tabs_from_page:
            tab_links.append(tab.find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))

        if not driver.find_elements(By.CLASS_NAME, 'BvSfz'):
            break
        page += 1
        driver.find_element(By.CLASS_NAME, 'BvSfz').click()

    print(f'Found {len(tab_links)} Powertab Files')
    return tab_links


def create_artist_folder(artist: str) -> str:
    """Build a path to the artist's folder, inside of Tabs where the files will be downloaded. First, builds path,
    and then determines if there's a folder there already. If not, creates folder. Returns the path to the folder."""
    dl_path = str(Path.cwd()) + '\\Tabs\\' + artist
    if path.isdir(dl_path):
        print("Using folder at " + dl_path)
        return dl_path
    try:
        mkdir(dl_path)
    except OSError as error:
        print(error)
    else:
        print("Folder created at " + dl_path)
    return dl_path  # return path so GUI can set download directory in browser


def scroll_to_bottom(driver: webdriver):
    """scrolls to the bottom of the page, twice, to deal with the browser 'bouncing' upwards as elements load."""
    # todo check if times can be cut/shortened
    sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
    sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
    sleep(.1)


def scroll_to_bottom_and_click_button(driver: webdriver, button_text: str):
    # Alternatively, use scrollIntoView to scroll the button into view
    button = driver.find_element_by_xpath(f"//button[contains(text(), '{button_text}')]")
    driver.execute_script("arguments[0].scrollIntoView();", button)
    button.click()


def get_tabs(driver: webdriver) -> list:
    """don't use this anymore"""
    tab_links = collect_links_guitar_pro(driver)
    # download for each element, skipping pro or official
    download_count, failure_count = 0, 0
    for i in range(len(tab_links)):
        tries = 0
        while True:  # used to restart iterations of for loop
            tries += 1
            if tries > 8:  # Count # of tries for current file, to prevent getting stuck
                print('Too many download attempts, moving on.')
                # GUI.failure_log_failed_attempt(tab_links[i])
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
                    sleep(.65)  # think this can go down to .5 at least todo optimize
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
    sleep(.5)
    return [download_count, failure_count]
