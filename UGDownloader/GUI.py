import sys
from datetime import datetime
from os import path, mkdir
from time import sleep
from pathlib import Path
import PySimpleGUI as sg
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import requests
import DLoader

THREAD_KEY = '-THREAD-'
DL_START_KEY = '-START DOWNLOAD-'
DL_COUNT_KEY = '-COUNT-'
DL_END_KEY = '-END DOWNLOAD-'
DL_THREAD_EXITING = '-THREAD EXITING-'
VERSION = 1.5


class GUI:
    EXITING = False
    CANCELED = False

    def __init__(self):
        folder_check()
        todl_data = get_todl_data()

        # start layout
        left_column = [
            [sg.Text(text='Artist', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-ARTIST-"),
             sg.Button(button_text='Save Info'), sg.Checkbox('Bypass cookies (E.U.), Chrome', default=False, key="-COOKIES-")],
            [sg.Text(text='Username', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-USERNAME-"),
             sg.Button(button_text='Autofill'), sg.Checkbox('Run in background', default=True, key="-HEADLESS-")],
            [sg.Text(text='Password', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-PASSWORD-"),
             sg.Button(button_text='Download'),
             sg.Combo(values=('Guitar Pro', 'Powertab', 'Both'), default_value='Guitar Pro', key="-FILETYPE-"),
             sg.Combo(values=('Chrome', 'Firefox'), default_value='Chrome', key="-BROWSER-")],
            [sg.Text(text='Progress'), sg.ProgressBar(100, 'h', size=(30, 20), key='-PROGRESS-', expand_x=True)],
            [sg.HSeparator()],
            [sg.Multiline(size=(60, 11), font='Courier 8', expand_x=True, expand_y=True,
                          write_only=True, reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True,
                          autoscroll=True, auto_refresh=True)],
            [sg.HSeparator()],
            [sg.Button(button_text='Copy Artist Name'), sg.Button(button_text='Add'), sg.Button(button_text='Delete'),
             sg.Input(size=(35, 1), pad=(0, 10), key="-TODLINPUT-")],
            [sg.Table(values=todl_data[:], num_rows=9, headings=['Artists to Download'],
                      key="-TODLTABLE-", enable_events=True, justification='center', expand_x=True)]

        ]

        right_column = [
            [sg.Text(size=(30, 4), justification='left',
                     text="-Artist entered must be an exact, case sensitive match to what Ultimate "
                          "Guitar has listed.")],
            [sg.Text(size=(30, 4), justification='left',
                     text="-Files will be downloaded to the folder this program is in.")],
            [sg.Text(size=(30, 4), justification='left', text='-You will need Chrome or firefox installed, select '
                                                              'which one you have.')],
            [sg.Text(size=(30, 6), justification='left',
                     text="-Ultimate Guitar requires a login to download tabs. If you just created an account, "
                          "you may have to wait a day or two for the captcha to stop appearing (this program won't "
                          "work while that's appearing).")],
            [sg.HSeparator(pad=((0, 0), (150, 10)))],
            [sg.Button(button_text='Cancel Download', expand_x=True)],
            [sg.Button(button_text='Exit', expand_x=True)]
        ]

        # ----- Full layout -----
        layout = [
            [
                sg.Column(left_column),
                sg.VSeperator(),
                sg.Column(right_column, vertical_alignment='top')
            ]
        ]
        # end layout

        window = sg.Window("Ultimate Guitar Downloader", layout)

        downloading = False
        window.finalize()
        check_update()

        # Run loop start
        while True:
            event, values = window.read()

            if event == "Save Info":
                save_user_info(values['-USERNAME-'], values['-PASSWORD-'])

            if event == "Autofill":
                autofill_user(window)

            if event == "Download" and not downloading:
                artist, user, password = values['-ARTIST-'], values['-USERNAME-'], values['-PASSWORD-']

                if not validate(artist, user, password):
                    continue

                driver = start_browser(artist, values['-HEADLESS-'], values['-BROWSER-'], values['-COOKIES-'])
                try:
                    window.start_thread(lambda: start_download
                    (driver, artist, user, password, window, values['-FILETYPE-']),
                                        (THREAD_KEY, DL_THREAD_EXITING))
                except Exception as e:
                    print(e)
                    driver.quit()
                    sg.popup_error("Something went wrong with the download. Try again- The most common problem is that"
                                   "the artist is not typed in exactly the way UG expects it, or the artist has no"
                                   "guitar pro files available. Other errors possible.")

            if event == "Copy Artist Name":
                copy_artist_name(window, values, todl_data)

            if event == "Add":
                add_to_todl_list(window, values)
                todl_data = get_todl_data()

            if event == "Delete":
                delete_from_todl(window, values, todl_data)
                todl_data = get_todl_data()

            if event == "Cancel Download":
                print('Canceling...')
                GUI.CANCELED = True
            if event == "Exit" or event == sg.WIN_CLOSED:
                print('Exiting.')

                GUI.EXITING = True
                break

            # thread events
            elif event[0] == THREAD_KEY:
                if event[1] == DL_START_KEY:
                    max_value = values[event]
                    downloading = True
                    window['-PROGRESS-'].update(0, max_value)
                elif event[1] == DL_COUNT_KEY:
                    window['-PROGRESS-'].update(values[event], max_value)
                elif event[1] == DL_END_KEY:
                    downloading = False
                elif event[1] == DL_THREAD_EXITING:
                    pass
        window.close()
        try:
            driver.quit()  # Still exits very slowly but at least it's behind the scenes
        except Exception as e:
            pass


def start_browser(artist: str, headless: bool, which_browser: str, no_cookies: bool) -> webdriver:
    dl_path = DLoader.create_artist_folder(artist)
    if which_browser == 'Firefox':
        ff_options = set_firefox_options(dl_path, headless, no_cookies)
        print(f'Starting Firefox, downloading latest Gecko driver.')
        driver = webdriver.Firefox(options=ff_options,
                                   service=FirefoxService(GeckoDriverManager(path='_UGDownloaderFiles').install()))
        # driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')  # get local copy of driver
        print('\n')

    if which_browser == 'Chrome':
        c_options = set_chrome_options(dl_path, headless, no_cookies)
        print(f'Starting Chrome, downloading latest chromedriver.')
        # driver = webdriver.Chrome(options=c_options, executable_path='chromedriver.exe')  # gets local copy of driver
        driver = webdriver.Chrome(options=c_options,
                                  service=ChromeService(ChromeDriverManager(path='_UGDownloaderFiles').install()))
        # next three lines allow chrome to download files while in headless mode
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
        driver.execute("send_command", params)
        print('\n')
    driver.which_browser = which_browser
    return driver


def autofill_user(window: sg.Window):
    # dummy account: user=mygoodusername, pass=passyword
    userinfo = open('_UGDownloaderFiles/userinfo.txt', 'r')
    data = ''
    for line in userinfo:
        data = line.split()
    if len(data) == 2:
        window["-USERNAME-"].update(data[0])
        window["-PASSWORD-"].update(data[1])
    else:
        print('There is either no user info saved or the data saved is invalid.')


def set_firefox_options(dl_path: str, headless: bool, no_cookies: bool) -> FFOptions:
    firefox_options = FFOptions()
    firefox_options.set_preference("browser.download.folderList", 2)
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.set_preference("browser.download.dir", dl_path)
    firefox_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    firefox_options.set_preference('permissions.default.stylesheet', 2)
    firefox_options.set_preference('permissions.default.image', 2)
    firefox_options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    if no_cookies:
        print('Currently, no cookies pop-up removing add-on is included for Firefox, please try Chrome instead if you '
              'are having cookies pop-up problems.\n')
    if headless:
        firefox_options.headless = True

    return firefox_options


def set_chrome_options(dl_path: str, headless: bool, no_cookies: bool) -> COptions:
    chrome_options = COptions()
    chrome_options.add_argument('--no-sandbox')  # not sure why this makes it work better
    preferences = {"download.default_directory": dl_path,  # pass the variable
                   "download.prompt_for_download": False,
                   "directory_upgrade": True,
                   # optimizations
                   "profile.managed_default_content_settings.images": 2,
                   "profile.default_content_setting_values.notifications": 2,
                   "profile.managed_default_content_settings.stylesheets": 2,
                   "profile.managed_default_content_settings.plugins": 2,
                   "profile.managed_default_content_settings.popups": 2,
                   "profile.managed_default_content_settings.geolocation": 2,
                   "profile.managed_default_content_settings.media_stream": 2}
    chrome_options.add_experimental_option('prefs', preferences)
    # to add I don't care about cookies, only works when headless is disabled
    if no_cookies:
        chrome_options.add_extension(fetch_resource('_UGDownloaderFiles/extension_3_4_6_0.crx'))
    elif headless:
        chrome_options.headless = True
    return chrome_options


def start_download(driver: webdriver, artist: str, user: str, password: str, window: sg.Window, file_type_wanted: str):
    # create log of download attempt
    failure_log_new_attempt()
    # first search for artist
    driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
    # setting the window size seems to help some element obfuscation issues
    driver.set_window_size(1100, 1000)
    # Then, click on artist from search results
    try:
        driver.find_element(By.LINK_TEXT, artist).click()
    except (TypeError, selenium.common.exceptions.NoSuchElementException):
        print("Cannot find artist. Did you type it in with the exact spelling and capitalization?\n")
        return
    if driver.which_browser == 'Firefox':
        sleep(1)

    login(driver, user, password)
    download_count, failure_count, tab_links = 0, 0, []

    print('Grabbing urls of requested files.')
    tab_links = DLoader.link_handler(driver, tab_links, file_type_wanted)

    print(f'Attempting {len(tab_links)} downloads.')
    window.write_event_value((THREAD_KEY, DL_START_KEY), len(tab_links))
    tabs_attempted = 0
    for link in tab_links:
        # download interruptions
        if GUI.EXITING:
            driver.quit()
            break
        if GUI.CANCELED:
            window.write_event_value((THREAD_KEY, DL_END_KEY), download_count)
            GUI.CANCELED = False
            driver.quit()
            print('Download canceled.')
            return
        results = DLoader.download_tab(driver, link)
        # try again after failure, 3 tries. Results[0] == 1 means a download was made
        tries = 1
        while results[0] == 0 and tries < 3:
            tries += 1
            print(f'Download failed, trying again. Attempt {tries}')
            temp = DLoader.download_tab(driver, link)
            results[0] += temp[0]
            results[1] += temp[1]
        if tries >= 3:
            failure_log_failed_attempt(link)
            print(f'Too many download attempts. Moving on')
        tabs_attempted += 1
        download_count += results[0]
        failure_count += results[1]
        window.write_event_value((THREAD_KEY, DL_COUNT_KEY), tabs_attempted)
    driver.quit()
    print(f'Downloads Finished. Total number of downloads: {str(download_count)}.')
    print(f'Total number of failures: {str(failure_count)}')
    window.write_event_value((THREAD_KEY, DL_END_KEY), len(tab_links))


def failure_log_new_attempt():
    with open('_UGDownloaderFiles/failurelog.txt', 'a+') as failurelog:
        failurelog.write(f"\nDownload attempt at: {str(datetime.now())}\n")
        failurelog.write(f"URLs of failed downloads:\n")


def failure_log_failed_attempt(text: str):
    with open('_UGDownloaderFiles\\failurelog.txt', 'a') as failurelog:
        failurelog.write(text + '\n')


def login(driver: webdriver, user: str, password: str):
    driver.find_element(By.CSS_SELECTOR, '.exTWY').click()  # login button
    sleep(1)
    form = driver.find_element(By.CSS_SELECTOR, "form > div.PictU")
    username_textbox = form.find_element(By.CSS_SELECTOR, 'input[name=username]')
    password_textbox = form.find_element(By.CSS_SELECTOR, 'input[name=password]')
    submit_button = form.find_element(By.CSS_SELECTOR, 'button[type=submit]')
    username_textbox.send_keys(user)
    password_textbox.send_keys(password)
    sleep(1)
    submit_button.click()
    # call method from captcha class, if figure out how to bypass captcha
    # this popup sometimes takes some time to appear, wait until it's clickable
    element = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR,
                                    'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)')))
    element.click()
    sleep(.5)
    print('Logged in')


def validate(artist: str, user: str, password: str) -> bool:
    if not artist:
        sg.popup_error('Artist cannot be blank.')
        return False
    if not user:
        sg.popup_error('Username cannot be blank.')
        return False
    if not password:
        sg.popup_error('Password cannot be blank.')
        return False
    return True


def folder_check():
    # makes sure that the Tabs folder and the userinfo.txt files exist
    if not path.isdir('Tabs'):
        mkdir('Tabs')
    if not path.isdir('_UGDownloaderFiles'):
        mkdir('_UGDownloaderFiles')
    if not path.isfile('_UGDownloaderFiles/userinfo.txt'):
        with open('_UGDownloaderFiles/userinfo.txt', 'x'):
            pass
    if not path.isfile('_UGDownloaderFiles/todownload.txt'):
        with open('_UGDownloaderFiles/todownload.txt', 'x'):
            pass


def get_todl_data() -> list:
    with open("_UGDownloaderFiles\\todownload.txt", 'r') as f:
        todl_data = [[line.rstrip()] for line in f]
    return todl_data


def add_to_todl_list(window: sg.Window, values: dict):
    if not values['-TODLINPUT-']:
        print('No artist to add. Please type one in the input box.')
        return
    with open('_UGDownloaderFiles/todownload.txt', 'a') as file:
        file.write('\n' + values['-TODLINPUT-'])
    todl_data = get_todl_data()
    print(f'New artist added to download list: {values["-TODLINPUT-"]}')
    window['-TODLTABLE-'].update(values=todl_data[:])


def delete_from_todl(window: sg.Window, values: dict, todl_data: list):
    selected_index = values['-TODLTABLE-'][0]
    if selected_index:
        print(f'Removed {todl_data.pop(selected_index)[0]} from to download list.')
        window['-TODLTABLE-'].update(values=todl_data[:])
        # todo not tested
        with open('_UGDownloaderFiles/todownload.txt', 'w+') as file:
            for i in range(len(todl_data)):
                file.write(todl_data[i][0])
                if i < len(todl_data) - 1:
                    file.write('\n')


def copy_artist_name(window: sg.Window, values: dict, todl_data: list):
    if not values['-TODLTABLE-']:
        print('Nothing selected.')
        return
    selected_artist = todl_data[values['-TODLTABLE-'][0]][0]
    window["-ARTIST-"].update(selected_artist)


def save_user_info(user, password):
    if not validate('A', user, password):
        return  # faked artist field to not trip validate
    with open('_UGDownloaderFiles/userinfo.txt', 'w+') as userinfo:
        userinfo.write(f'{user} {password}')
    print(f'New User info saved.')


def fetch_resource(resource_path: Path) -> Path:
    """Grabs resource from local path when running as a script, grabs from a temp directory when running
        as a pyinstaller .exe. Keeps hardcoded relative paths intact. Use with pyinstaller '--add-data command
        to add data files."""
    try:  # running as *.exe; fetch resource from temp directory
        base_path = Path(sys._MEIPASS)
    except AttributeError:  # running as script; return unmodified path
        return resource_path
    else:  # return temp resource path
        return base_path.joinpath(resource_path)


def check_update():
    # Make a request to the GitHub API to get the releases
    api_url = f"https://api.github.com/repos/jabbey1/UGDownloader/releases"
    response = requests.get(api_url)
    print('Checking for updated .exe release.')
    # Check if the request was successful
    if response.status_code == 200:
        releases = response.json()
        # Get the latest release
        latest_release_version = releases[0]["tag_name"]  # Assumes the API returns releases in descending order
        if latest_release_version != str(VERSION):
            print(f"A new release is available: {latest_release_version}. Current version: {VERSION}")
            print("https://github.com/jabbey1/UGDownloader/releases\n")

        else:
            print(f"No new release found. Current version: {VERSION}")
    else:
        print("Error occurred while checking for update.")
