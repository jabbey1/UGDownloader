import os
import time
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import DLoader
import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService


class GUI:

    def __init__(self):
        folder_check()
        todl_data = get_todl_data()

        # start layout
        left_column = [
            [sg.Text(text='Artist', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-ARTIST-"),
             sg.Button(button_text='Save Info')],
            [sg.Text(text='Username', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-USERNAME-"),
             sg.Button(button_text='Autofill'), sg.Checkbox('Run in background', default=True, key="-HEADLESS-")],
            [sg.Text(text='Password', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-PASSWORD-"),
             sg.Button(button_text='Download'), sg.Combo(values=('Chrome', 'Firefox'), default_value='Chrome',
                                                         key="-BROWSER-")],
            [sg.HSeparator()],
            [sg.Multiline(size=(60, 11), font='Courier 8', expand_x=True, expand_y=True,
                          write_only=True, reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True,
                          autoscroll=True, auto_refresh=True)],
            [sg.HSeparator()],
            [sg.Button(button_text='Copy Artist Name'), sg.Button(button_text='Add'), sg.Button(button_text='Delete'),
             sg.Input(size=(35, 1), pad=(0, 10), key="-TODLINPUT-")],
            [sg.Table(values=todl_data[:], num_rows=9, headings=['Artists to Download'],
                      key="-TODLTABLE-", enable_events=True)]  # enable_click_events=True

        ]

        right_column = [
            [sg.Text(size=(30, 5), justification='center',
                     text="-Artist entered must be an exact, case sensitive match to what Ultimate "
                          "Guitar has listed.")],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Files will be downloaded to the folder this program is in.")],
            [sg.Text(size=(30, 5), justification='center', text='-You will need Chrome or firefox installed, select '
                                                                'which one you have.')],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Ultimate Guitar requires a login to download tabs. If you just created an account, "
                          "you may have to wait a day or two for the captcha to stop appearing (this program won't"
                          "work while that's appearing).")],
            [sg.HSeparator()],
            [sg.Text()],
            # [sg.HSeparator()],
            [sg.Button(button_text='Exit')]
        ]

        # ----- Full layout -----
        layout = [
            [
                sg.Column(left_column),
                sg.VSeperator(),
                sg.Column(right_column),
            ]
        ]
        # end layout

        window = sg.Window("Ultimate Guitar Downloader", layout)
        # Run loop start
        while True:
            event, values = window.read()
            if event == "Save Info":
                save_user_info(values)

            if event == "Autofill":
                autofill_user(window)

            if event == "Download":
                artist, user, password = values['-ARTIST-'], values['-USERNAME-'], values['-PASSWORD-']

                if not validate(artist, user, password):
                    continue

                driver = start_browser(artist, values['-HEADLESS-'], values['-BROWSER-'])
                try:
                    start_download(driver, artist, user, password)
                    driver.quit()
                    sg.popup('Downloads finished.')
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

            if event == "Exit" or event == sg.WIN_CLOSED:
                break
        window.close()


def start_browser(artist: str, headless: bool, which_browser: str) -> webdriver:
    dl_path = DLoader.create_artist_folder(artist)
    if which_browser == 'Firefox':
        ff_options = set_firefox_options(dl_path, headless)
        print(f'Starting Firefox, downloading latest Gecko driver.')
        driver = webdriver.Firefox(options=ff_options,
                                   service=FirefoxService(GeckoDriverManager(path='_UGDownloaderFiles').install()))
        # driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')  # get local copy of driver
        print('\n')

    if which_browser == 'Chrome':
        c_options = set_chrome_options(dl_path, headless)
        print(f'Starting Chrome, downloading latest chromedriver.')
        # driver = webdriver.Chrome(options=c_options, executable_path='chromedriver.exe')  # gets local copy of driver
        driver = webdriver.Chrome(options=c_options,
                                  service=ChromeService(ChromeDriverManager(path='_UGDownloaderFiles').install()))
        # next three lines are allowing chrome to download files while in headless mode
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
        command_result = driver.execute("send_command", params)
        print('\n')
    driver.which_browser = which_browser
    return driver


def autofill_user(window):
    # dummy account: user=mygoodusername, pass=passyword
    userinfo = open('_UGDownloaderFiles/userinfo.txt', 'r')
    data = ''
    for line in userinfo:
        data = line.split()
    if len(data) == 2:
        window["-USERNAME-"].update(data[0])
        window["-PASSWORD-"].update(data[1])
    else:
        print(f'There is either no user info saved or the data saved is invalid.')


def set_firefox_options(dl_path: str, headless: bool) -> FFOptions:
    ff_options = FFOptions()
    ff_options.set_preference("browser.download.folderList", 2)
    ff_options.set_preference("browser.download.manager.showWhenStarting", False)
    ff_options.set_preference("browser.download.dir", dl_path)
    ff_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    ff_options.set_preference('permissions.default.stylesheet', 2)
    ff_options.set_preference('permissions.default.image', 2)
    ff_options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')
    # possible cookie fix
    # ff_options.set_preference("network.cookie.cookieBehavior", 2)
    if headless:
        ff_options.headless = True

    return ff_options


def set_chrome_options(dl_path: str, headless: bool) -> COptions:
    c_options = COptions()
    c_options.add_argument('--no-sandbox')  # not sure why this makes it work better
    preferences = {"download.default_directory": dl_path,  # pass the variable
                   "download.prompt_for_download": False,
                   "directory_upgrade": True,
                   # optimizations
                   "profile.managed_default_content_settings.images": 2,
                   "profile.default_content_setting_values.notifications": 2,
                   "profile.managed_default_content_settings.stylesheets": 2,
                   # possible cookies fix?
                   # 2 blocks all cookies, 1 just blocks 3rd party
                   # "profile.managed_default_content_settings.cookies": 2,
                   # not sure how this line behaves differently than previous
                   # "profile.block_third_party_cookies": True,
                   # "profile.managed_default_content_settings.javascript": 1,
                   "profile.managed_default_content_settings.plugins": 2,
                   "profile.managed_default_content_settings.popups": 2,
                   "profile.managed_default_content_settings.geolocation": 2,
                   "profile.managed_default_content_settings.media_stream": 2}
    c_options.add_experimental_option('prefs', preferences)
    # to add I don't care about cookies, something like:
    # c_options.add_extension(r'_UGDownloaderFiles/extension_3_4_6_0.crx')
    if headless:
        c_options.headless = True
    return c_options


def start_download(driver: webdriver, artist: str, user: str, password: str):
    # create log of download attempt
    failure_log_new_attempt()
    # navigate to site, go to artist page, then filter out text tabs
    # first search for artist
    driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
    # setting the window size seems to help some element obfuscation issues
    driver.set_window_size(1100, 1000)
    # Then, click on artist from search results
    driver.find_element(By.LINK_TEXT, artist).click()
    if driver.which_browser == 'Firefox':
        time.sleep(1)
    # Click on the Guitar Pro tab to go to page with only GP, 'Official', and 'Pro' tabs
    driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
    login(driver, user, password)
    print('Starting downloads...')
    download_count, failure_count = 0, 0
    # get list of tabs, ignoring non GP files, then iterate thru list downloading each one
    tab_links = DLoader.collect_links(driver)
    for link in tab_links:
        results = DLoader.download_tab(driver, link)
        # try again after failure, 8 tries. Results[0] == 1 means a download was made
        tries = 1
        while results[0] == 0 and tries < 8:
            tries += 1
            print(f'Download failed, trying again. Attempt {tries}')
            temp = DLoader.download_tab(driver, link)
            results[0] += temp[0]
            results[1] += temp[1]
        if tries >= 8:
            print(f'Too many download attempts. Moving on')
        download_count += results[0]
        failure_count += results[1]

    print(f'Downloads Finished. Total number of downloads: {str(download_count)}.')
    print(f'Total number of failures: {str(failure_count)}')


def failure_log_new_attempt():
    # create log of download attempt
    failurelog = open('_UGDownloaderFiles\\failurelog.txt', 'a+')
    failurelog.write('\n')
    failurelog.write('Download attempt at:' + str(datetime.datetime.now()))
    failurelog.write('\n')
    failurelog.close()


def login(driver: webdriver, user: str, password: str):
    driver.find_element(By.CSS_SELECTOR, '.exTWY').click()  # login button
    time.sleep(1)
    form = driver.find_element(By.CSS_SELECTOR, "form > div.PictU")
    username_textbox = form.find_element(By.CSS_SELECTOR, 'input[name=username]')
    password_textbox = form.find_element(By.CSS_SELECTOR, 'input[name=password]')
    submit_button = form.find_element(By.CSS_SELECTOR, 'button[type=submit]')
    username_textbox.send_keys(user)
    password_textbox.send_keys(password)
    time.sleep(1)
    submit_button.click()
    # call method from captcha class, if figure out how to bypass captcha
    # this popup sometimes takes some time to appear, wait until it's clickable
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                    'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)')))
    element.click()
    time.sleep(.5)
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
    if not os.path.isdir('Tabs'):
        os.mkdir('Tabs')
    if not os.path.isdir('_UGDownloaderFiles'):
        os.mkdir('_UGDownloaderFiles')
    if not os.path.isfile('_UGDownloaderFiles/userinfo.txt'):
        with open('_UGDownloaderFiles/userinfo.txt', 'x'):
            pass
    if not os.path.isfile('_UGDownloaderFiles/todownload.txt'):
        with open('_UGDownloaderFiles/todownload.txt', 'x'):
            pass


def get_todl_data() -> list:
    with open("_UGDownloaderFiles\\todownload.txt", 'r') as f:
        todl_data = [[line.rstrip()] for line in f]
    return todl_data


def add_to_todl_list(window, values):
    if not values['-TODLINPUT-']:
        print('No artist to add. Please type one in the input box.')
        return
    else:
        file = open('_UGDownloaderFiles/todownload.txt', 'a')
        file.write('\n')
        new_artist = values['-TODLINPUT-']
        file.write(new_artist)
        file.close()
        todl_data = get_todl_data()
        print(f'New artist added to To Download: {new_artist}')
    window['-TODLTABLE-'].update(values=todl_data[:])


def delete_from_todl(window, values, todl_data):
    selected_index = values['-TODLTABLE-'][0]
    if selected_index:
        print(f' removed {todl_data.pop(selected_index)} from to download list.')
        window['-TODLTABLE-'].update(values=todl_data[:])
        file = open('_UGDownloaderFiles/todownload.txt', 'w+')
        for i in range(len(todl_data)):
            file.write(todl_data[i][0])
            if i < len(todl_data) - 1:
                file.write('\n')
        file.close()


def copy_artist_name(window, values, todl_data):
    if not values['-TODLTABLE-']:
        print('Nothing selected.')
        return
    selected_artist = todl_data[values['-TODLTABLE-'][0]][0]
    window["-ARTIST-"].update(selected_artist)


def save_user_info(values):
    user, password = values['-USERNAME-'], values['-PASSWORD-']
    if not validate('A', user, password):
        return  # faked artist field to not trip validate
    userinfo = open('_UGDownloaderFiles/userinfo.txt', 'w+')
    userinfo.write(user)
    userinfo.write(' ')
    userinfo.write(password)
    userinfo.close()
    print(f'New User info saved.')
