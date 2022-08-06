from pathlib import Path
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
import PySimpleGUI as sg
import DLoader
from selenium.webdriver.common.by import By


class GUI:

    def __init__(self):

        # start layout
        left_column = [
            [sg.Text(text='Artist', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-ARTIST-")],
            [sg.Text(text='Username', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-USERNAME-")],
            [sg.Text(text='Password', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-PASSWORD-"),
             sg.Button(button_text='Download')],
            # [sg.HSeparator()],
            # [sg.FolderBrowse()],
            # [sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-FILE LIST-")],
        ]

        right_column = [
            [sg.Text(size=(30, 5), justification='center',
                     text="-Artist entered must be an exact, case sensitive match to what Ultimate "
                          "Guitar has listed.")],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Files will be downloaded to the folder this program is in.")],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Ultimate Guitar requires a login to download tabs.")],
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
        # todo move gui logic to main?
        while True:
            event, values = window.read()
            if event == "Download":
                # todo create download folder, set options. download dir,
                # todo remove placeholder artist, login input
                artist = 'Wormrot'
                user = 'jake.c.abbey5555'
                password = '!bRD3*@erWRZ54'
                driver = start_browser(artist)
                start_download(driver, artist, user, password)

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

        window.close()


# todo check validity of all text entries
# todo download button press

def start_browser(artist):
    # find path of Tabs folder, and set browser options
    dl_path = str(Path.cwd())
    dl_path += '\\Tabs\\'
    dl_path += artist
    DLoader.create_artist_folder(dl_path)
    # setup browser options
    options = Options()
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", dl_path)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    # todo return the driver object
    driver = webdriver.Firefox(options=options)  # create instance of browser
    return driver


# deal with placeholder user/pass input
def start_download(driver, artist, user, password):
    # navigate to site, go to artist page, then filter out text tabs
    driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
    driver.find_element(By.LINK_TEXT, artist).click()
    driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
    # Login required...
    driver.find_element(By.CSS_SELECTOR, '.exTWY > span:nth-child(1)').click()  # login button
    username_textbox = driver.find_element(By.CSS_SELECTOR, '.wzvZg > div:nth-child(1) > input:nth-child(1)')
    password_textbox = driver.find_element(By.CSS_SELECTOR, '.wlfii > div:nth-child(1) > input:nth-child(1)')
    username_textbox.send_keys(user)
    password_textbox.send_keys(password)
    password_textbox.send_keys(Keys.RETURN)
    print('logged in hopefully')
    if driver.find_element(By.CSS_SELECTOR, '.IqBxG'):
        sg.popup_error(title='Login Error')
        print('login error')
        return
    # todo if found element of the login area still around, then login failed
    # Click out of annoying popup
    driver.find_element(By.CSS_SELECTOR,
                        'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)').click()
    current_page = driver.current_url
    while True:
        DLoader.get_tabs(driver)
        driver.get(current_page)
        if driver.find_elements(By.CLASS_NAME, 'BvSfz'):
            print("There's another page")
            driver.find_element(By.CLASS_NAME, 'BvSfz').click()
            current_page = driver.current_url
            continue
        else:
            driver.close()
            break
