from re import search
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
import Tab
from Utils import config

DOWNLOAD_BUTTON_SELECTOR = config.get('Selectors', 'DOWNLOAD_BUTTON_SELECTOR')
TAB_BLOCKED_SELECTOR = config.get('Selectors', 'TAB_BLOCKED_SELECTOR')
TAB_ROW_SELECTOR = config.get('Selectors', 'TAB_ROW_SELECTOR')
TAB_LINK_CONTAINER = config.get('Selectors', 'TAB_LINK_CONTAINER')
MY_TABS_ROW_SELECTOR = config.get('Selectors', 'MY_TABS_ROW_SELECTOR')
TAB_TEXT_SELECTOR = config.get('Selectors', 'TAB_TEXT_SELECTOR')
TAB_TYPE_SELECTOR = config.get('Selectors', 'TAB_TYPE_SELECTOR')
NEXT_PAGE_SELECTOR = config.get('Selectors', 'NEXT_PAGE_SELECTOR')
USER_TABS_TABLE_SELECTOR = config.get('Selectors', 'USER_TABS_TABLE_SELECTOR')
USER_NEXT_PAGE_SELECTOR = config.get('Selectors', 'USER_NEXT_PAGE_SELECTOR')



def download_tab(driver: webdriver, tab: Tab.Tab) -> List[int]:
    """Download the file. Navigates to page and clicks download button. If the tab is blocked, the fallback method
    is called (unlikely to work). Returns values to keep track of total number of downloads and failures
    """
    download_count, failure_count = 0, 0
    if driver.current_url != tab.url:
        driver.get(tab.url)

    if is_tab_blocked(driver):
        print('This tab has been blocked. Now trying fallback download method, may or may not be successful.')
        download_tab_fallback(driver, tab.url)
        # increments download count regardless of whether it downloads, as we don't want to loop thru additional
        # downloads
        download_count += 1
        return [download_count, failure_count]

    print(f'Downloading tab @ {tab.url}')

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
    """Call after navigating driver the page of the tab you want to check.
    """
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


def download_text(driver: webdriver, url: str) -> str:
    """ Download the raw text of the tab
    """
    if driver.current_url != url:
        driver.get(url)
    print(f'Downloading tab text @ {url}')
    # get html of element matching TAB_TEXT_SELECTOR
    wait = WebDriverWait(driver, 5)  # Timeout after 10 seconds
    tab_text_element = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, TAB_TEXT_SELECTOR)))
    tab_text_raw = tab_text_element.text
    return tab_text_raw


def click_tab_type(driver: webdriver, tab_type: str, my_tabs_wanted: bool):
    """Clicks on the tab type link on the artist page. This is used to navigate to the page with the list of tabs
    for the artist. The type is the name of the tab type, such as 'Guitar Pro', 'Power', 'Chords', etc."""
    if my_tabs_wanted:
        if tab_type == 'Guitar Pro' or tab_type == 'Power':
            tab_type = 'Pro'
        elif tab_type == 'Tab':
            tab_type = 'Tabs'
        elif tab_type == 'Bass':
            tab_type = 'Bass Tabs'

        xpath = TAB_TYPE_SELECTOR + tab_type + "']"
        button = driver.find_element(By.XPATH, xpath)
        button.click()
    else:
        driver.find_element(By.LINK_TEXT, tab_type).click()


def link_handler(driver: webdriver, tab_list: list[Tab.Tab], file_type_wanted: str,
                 search_type: str, artist: str) -> list:
    """Take a list and call methods to add tabs to tab_list. Driver must be navigated to artist
    page. Will navigate to filetype filtered page before handing off to collect_links"""
    my_tabs_wanted = search_type == 'My Tabs'
    # Download from user
    if search_type == 'User':
        return collect_links_user(driver, file_type_wanted, tab_list)

    # Guitar Pro tabs
    if file_type_wanted in ('Guitar Pro', 'All', 'Pro + Power'):
        try:
            if my_tabs_wanted:
                driver.find_element(By.XPATH, "//nav[@class='Do1zZ ydHr1']//div[@role='button' and text()='Pro']").click()
            else:
                driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
            tab_list.extend(collect_links_guitar_pro(driver, True, file_type_wanted))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Guitar Pro tabs for this artist.')
    # Powertabs
    if file_type_wanted in ('Powertab', 'All', 'Pro + Power'):
        try:
            if my_tabs_wanted:
                driver.find_element(By.XPATH, "//nav[@class='Do1zZ ydHr1']//div[@role='button' and text()='Power']").click()
            else:
                driver.find_element(By.LINK_TEXT, 'Power').click()
            tab_list.extend(collect_links_powertab(driver, True, file_type_wanted))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Powertabs for this artist.')
    # Text tabs
    if file_type_wanted in ('Text', 'All'):
        try:
            click_tab_type(driver, 'Chords', my_tabs_wanted)
            tab_list.extend(collect_links_text(driver, True, 'Chords',
                                                       my_tabs_wanted, artist))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Chord tabs for this artist.')
        try:
            click_tab_type(driver, 'Tab', my_tabs_wanted)
            tab_list.extend(collect_links_text(driver, True, 'Tab',
                                                       my_tabs_wanted, artist))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Tab tabs for this artist.')
        try:
            click_tab_type(driver, 'Bass', my_tabs_wanted)
            tab_list.extend(collect_links_text(driver, True, 'Bass',
                                                       my_tabs_wanted, artist))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Bass tabs for this artist.')
        try:
            if my_tabs_wanted:
                pass  # Uke isn't supported in My Tabs
            else:
                click_tab_type(driver, 'Ukulele', my_tabs_wanted)
                tab_list.extend(collect_links_text(driver, True, 'Ukulele', my_tabs_wanted, artist))
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print('There are no available Ukulele tabs for this artist.')

    return tab_list


def collect_links_guitar_pro(driver: webdriver, verbose: bool, tab_type: str) -> list[Tab.Tab]:
    """ Collects guitar pro files only, page by page"""
    tab_list, page = [], 1

    while True:
        if verbose:
            print(f"Reading page {page} for {tab_type} tabs")
        links_from_page = [x for x in driver.find_elements(By.CLASS_NAME, TAB_ROW_SELECTOR) if 'Guitar Pro' in x.text]
        for link in links_from_page:
            url = link.find_element(By.CSS_SELECTOR, TAB_LINK_CONTAINER).get_attribute('href')
            tab_list.append(Tab.Tab(url))

        if not driver.find_elements(By.CLASS_NAME, NEXT_PAGE_SELECTOR):
            break
        page += 1
        driver.find_element(By.CLASS_NAME, NEXT_PAGE_SELECTOR).click()

    if verbose:
        print(f'Found {len(tab_list)} Guitar Pro Files\n')
    return tab_list


def collect_links_powertab(driver: webdriver, verbose: bool, tab_type: str) -> list:
    """ Collects powertab files only, page by page"""
    tab_list, page = [], 1

    while True:
        if verbose:
            print(f"Reading page {page} for {tab_type} tabs")
        links_from_page = [x for x in driver.find_elements(By.CLASS_NAME, TAB_ROW_SELECTOR) if 'Power' in x.text]
        for link in links_from_page:
            url = link.find_element(By.CSS_SELECTOR, TAB_LINK_CONTAINER).get_attribute('href')
            tab_list.append(Tab.Tab(url))

        if not driver.find_elements(By.CLASS_NAME, NEXT_PAGE_SELECTOR):
            print('Found no more pages.')
            break
        page += 1
        driver.find_element(By.CLASS_NAME, NEXT_PAGE_SELECTOR).click()

    if verbose:
        print(f'Found {len(tab_list)} Powertab Files\n')
    return tab_list


def collect_links_text(driver: webdriver, verbose: bool, tab_type: str,
                       my_tabs_wanted: bool, artist: str) -> list:
    """ Collects links to text files only, page by page"""
    tab_list, page = [], 1

    while True:
        if verbose:
            print(f"Reading page {page} for {tab_type} tabs")

        tabs_from_page_unfiltered = driver.find_elements(By.CLASS_NAME, TAB_ROW_SELECTOR)

        tab_list.extend(get_tab_info(tabs_from_page_unfiltered, tab_type,
                                     my_tabs_wanted, artist))

        # break
        if not driver.find_elements(By.CLASS_NAME, NEXT_PAGE_SELECTOR):
            break
        page += 1
        driver.find_element(By.CLASS_NAME, NEXT_PAGE_SELECTOR).click()

    if verbose:
        print(f'Found {len(tab_list)} {tab_type} files\n')
    return tab_list

def collect_links_user(driver: webdriver, file_type_wanted: str, tab_list: list[Tab.Tab]) -> list[Tab.Tab]:
    """Creates a set of wanted filetypes before collecting the tabs of each type."""
    page = 1
    wanted_set = set()
    if file_type_wanted == 'Guitar Pro':
        wanted_set = 'Guitar Pro'
    elif file_type_wanted == 'Powertab':
        wanted_set = 'Power'
    elif file_type_wanted == 'Pro + Power':
        wanted_set = 'Power', 'Guitar Pro'
    elif file_type_wanted == 'Text':
        wanted_set = 'Tab', 'Bass', 'Chords'

    while True:
        print(f"Reading page {page} for user tabs")
        tab_table = driver.find_element(By.CSS_SELECTOR, USER_TABS_TABLE_SELECTOR)
        tbody = tab_table.find_element(By.TAG_NAME, 'tbody')
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if cols[1].text in wanted_set or file_type_wanted == 'All':
                url = cols[0].find_element(By.TAG_NAME, 'a').get_attribute('href')
                tab_list.append(Tab.Tab(url))

        page += 1

        try:
            element = driver.find_element(By.CLASS_NAME, USER_NEXT_PAGE_SELECTOR)
            link = element.find_element(By.TAG_NAME, 'a').get_attribute('href')
            driver.get(link)
        except:
            break

    print(f'Found {len(tab_list)} user Files\n')
    return tab_list

def get_tab_info(tabs_from_page, tab_type: str, my_tabs_wanted: bool,
                 artist: str) -> list:
    tab_info_list = []
    for tab in tabs_from_page:
        last_artist = artist
        if tab_type in tab.text:
            parts = tab.text.split('\n')

            # determine if page is from My Tabs or not
            if my_tabs_wanted:
                if len(parts) == 2:
                    info_artist = last_artist
                    title = parts[0]
                else:
                    info_artist = parts[0]
                    last_artist = parts[0]
                    title = parts[1]
                tab_type = tab_type
            else:  # If not My Tabs, then the artist is the first part of the text
                info_artist = artist
                title = parts[0]
                tab_type = tab_type
            link = tab.find_element(By.CSS_SELECTOR, TAB_LINK_CONTAINER).get_attribute('href')
            new_tab = Tab.Tab(link)
            new_tab.artist = info_artist
            new_tab.song_name = title
            new_tab.format = tab_type

            tab_info_list.append(new_tab)
    return tab_info_list


def get_already_downloaded_count(artist: str):
    """Return the number of files you already have for a given artist"""
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


def new_tabs_checker(driver: webdriver, artist: str, filetype: str, search_type: str):
    """Compares the number files available online to the number of files that you have locally."""
    search_for_artist(driver, artist)
    count = get_already_downloaded_count(artist)
    tab_list = []
    tab_list = link_handler(driver, tab_list, filetype, search_type, artist)
    online_amount = len(tab_list)
    print(f'\nYour {artist} folder has {count} files.')
    print(f'Online, there are {online_amount} of type: {filetype} available.')
    print('\nClosing browser...')
    driver.quit()
    print('\nBrowser closed.')
