from typing import List
from time import sleep
import selenium.common.exceptions
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException
import Utils
from Utils import config

DOWNLOAD_BUTTON_SELECTOR = config.get('Selectors', 'DOWNLOAD_BUTTON_SELECTOR')
TAB_BLOCKED_SELECTOR = config.get('Selectors', 'TAB_BLOCKED_SELECTOR')
TAB_ROW_SELECTOR = config.get('Selectors', 'TAB_ROW_SELECTOR')
TAB_LINK_CONTAINER = config.get('Selectors', 'TAB_LINK_CONTAINER')
NEXT_PAGE_SELECTOR = config.get('Selectors', 'NEXT_PAGE_SELECTOR')


def download_tab(driver: webdriver, url: str) -> List[int]:
    """Download the file. Navigates to page, scrolls to the bottom where the download button is, and then clicks. If
    the click fails, or the button isn't there, the fallback method is called. Returns values to keep track of total
    number of downloads and failures"""
    download_count, failure_count = 0, 0
    driver.get(url)

    if is_tab_blocked(driver):
        print('This tab has been blocked. Now trying fallback download method, may or may not be successful.')
        download_tab_fallback(driver, url)
        # increments download count regardless of whether it downloads, as we don't want to loop thru additional
        # downloads
        download_count += 1
        return [download_count, failure_count]

    print(f'Downloading tab @ {url}')

    try:
        button = WebDriverWait(driver, 10).until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, DOWNLOAD_BUTTON_SELECTOR))
        )
        driver.execute_script('arguments[0].click();', button)
        # seem to need to give firefox time on page after a download
        if driver.which_browser == 'Firefox':
            sleep(.65)
        download_count += 1
    except NoSuchElementException:
        print("Is the button obscured or not clickable? Trying again.")
        failure_count += 1
    except Exception as e:  # sometimes the button is obscured by other elements, or button doesn't exist
        print('Error. Printing information below. Will try again.')
        print(e)
        failure_count += 1
    sleep(0.5)
    return [download_count, failure_count]


def is_tab_blocked(driver: webdriver) -> bool:
    # call after navigating to page that you want to check
    try:
        driver.find_element(By.CSS_SELECTOR, TAB_BLOCKED_SELECTOR)
        return True
    except NoSuchElementException:
        return False


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
    js_dl = f"window.location.href='https://tabs.ultimate-guitar.com/tab/download?id={uid}';"
    driver.execute_script(js_dl)
    sleep(.5)


def link_handler(driver: webdriver, tab_links: list, file_type_wanted: str) -> list:
    """Take a list and call methods to add links to tabs of requested filetypes. Driver must be navigated to artist
    page. Will navigate to filetype filtered page before handing off to collect_links"""
    if file_type_wanted in ('Guitar Pro', 'Both'):
        try:
            driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
            tab_links.extend(collect_links_guitar_pro(driver, True))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Guitar Pro tabs for this artist.')
    if file_type_wanted in ('Powertab', 'Both'):
        try:
            driver.find_element(By.LINK_TEXT, 'Power').click()
            tab_links.extend(collect_links_powertab(driver, True))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Powertabs for this artist.')
    elif file_type_wanted == 'Text':
        print("Not yet implemented")

    return tab_links


def collect_links_guitar_pro(driver: webdriver, verbose: bool) -> list:
    """ Collects links to guitar pro files only, page by page"""
    tab_links, page = [], 1

    while True:
        if verbose:
            print(f"Reading page {page}")
        tabs_from_page = [x for x in driver.find_elements(By.CLASS_NAME, TAB_ROW_SELECTOR) if 'Guitar Pro' in x.text]
        for tab in tabs_from_page:
            tab_links.append(tab.find_element(By.CSS_SELECTOR, TAB_LINK_CONTAINER).get_attribute('href'))

        if not driver.find_elements(By.CLASS_NAME, NEXT_PAGE_SELECTOR):
            break
        page += 1
        driver.find_element(By.CLASS_NAME, NEXT_PAGE_SELECTOR).click()

    if verbose:
        print(f'Found {len(tab_links)} Guitar Pro Files')
    return tab_links


def collect_links_powertab(driver: webdriver, verbose: bool) -> list:
    """ Collects links to powertab files only, page by page"""
    tab_links, page = [], 1

    while True:
        if verbose:
            print(f"Reading page {page}")
        tabs_from_page = [x for x in driver.find_elements(By.CLASS_NAME, TAB_ROW_SELECTOR) if 'Power' in x.text]
        for tab in tabs_from_page:
            tab_links.append(tab.find_element(By.CSS_SELECTOR, TAB_LINK_CONTAINER).get_attribute('href'))

        if not driver.find_elements(By.CLASS_NAME, NEXT_PAGE_SELECTOR):
            break
        page += 1
        driver.find_element(By.CLASS_NAME, NEXT_PAGE_SELECTOR).click()

    if verbose:
        print(f'Found {len(tab_links)} Powertab Files')
    return tab_links


def create_artist_folder(artist: str) -> Path:
    """Build a path to the artist's folder, inside of Tabs where the files will be downloaded. First, builds path,
    and then determines if there's a folder there already. If not, creates folder. Returns the path to the folder."""
    dl_path = Path(Utils.tab_download_path / artist)
    if dl_path.is_dir():
        print(f"Using folder at {dl_path}")
        return dl_path
    dl_path.mkdir(parents=True, exist_ok=True)
    print(f"Folder created at {dl_path}")
    return dl_path  # return path so GUI can set download directory in browser


def get_already_downloaded_count(artist: str):
    dl_path = Path(Utils.tab_download_path / artist)
    file_count = sum(1 for file in dl_path.iterdir() if file.is_file())
    return file_count


def scroll_to_bottom(driver: webdriver):
    """scrolls to the bottom of the page, twice, to deal with the browser 'bouncing' upwards as elements load."""
    sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
    sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
    sleep(.1)


def search_for_artist(driver: webdriver, artist: str):
    """ Navigates to the search page for a particular artist. Raises exception if it can't find artist. """

    search_url = Utils.search_url
    driver.get(search_url + artist)
    try:
        driver.find_element(By.LINK_TEXT, artist).click()
    except (TypeError, selenium.common.exceptions.NoSuchElementException):
        print("Cannot find artist. Did you type it in with the exact spelling and capitalization?\n")
        return
    if driver.which_browser == 'Firefox':
        sleep(1)


def new_tabs_checker(driver: webdriver, artist: str, filetype: str):
    search_for_artist(driver, artist)
    count = get_already_downloaded_count(artist)
    tab_links = []
    tab_links = link_handler(driver, tab_links, filetype)

    print(f'\nYour {artist} folder has {count} files.')
    print(f'Online, there are {len(tab_links)} of type: {filetype} available.')
    print('\nClosing browser...')
    driver.quit()
    print('Browser closed.')
