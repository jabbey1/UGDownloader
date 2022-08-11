import time
from pathlib import Path
import PySimpleGUI as sg
# from line_profiler_pycharm import profile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import DLoader


class GUI:

    # noinspection PyBroadException
    def __init__(self):

        # start layout
        left_column = [
            [sg.Text(text='Artist', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-ARTIST-")],
            [sg.Text(text='Username', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-USERNAME-"),
             sg.Button(button_text='Autofill')],
            [sg.Text(text='Password', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-PASSWORD-"),
             sg.Button(button_text='Download')],
            [sg.HSeparator()],
            [sg.Multiline(size=(60, 15), font='Courier 8', expand_x=True, expand_y=True,
                          write_only=True, reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True,
                          autoscroll=True, auto_refresh=True)
             # [sg.Output(size=(60,15), font='Courier 8', expand_x=True, expand_y=True)]
             ]
        ]

        right_column = [
            [sg.Text(size=(30, 5), justification='center',
                     text="-Artist entered must be an exact, case sensitive match to what Ultimate "
                          "Guitar has listed.")],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Files will be downloaded to the folder this program is in.")],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Ultimate Guitar requires a login to download tabs. If you just created an account, "
                          "you may have to wait a day or two for the captcha to stop appearing (this program won't"
                          "work while that's appearing).")],
            [sg.Text(size=(30, 5), justification='center',
                     text="-Autofill will automatically enter a dummy account, but no guarantees for how long"
                          "this will work for.")],
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
        while True:
            event, values = window.read()
            if event == "Autofill":
                # dummy account: user=mygoodusername, pass=passyword
                window["-USERNAME-"].update('mygoodusername')
                window["-PASSWORD-"].update('passyword')
            if event == "Download":
                artist = values['-ARTIST-']
                user = values['-USERNAME-']
                password = values['-PASSWORD-']
                if not validate(artist, user, password):
                    continue
                driver = start_browser(artist)
                # try:
                start_download(driver, artist, user, password)
                sg.popup('Downloads finished.')
                #todo make this exception print error
                # except:  # could track down each failure point to add exceptions for each
                #     driver.close()
                #     sg.popup_error("Something went wrong with the download. Try again- check that the "
                #                    "artist you entered is on the site, and has guitar pro tabs available.")

            if event == "Exit" or event == sg.WIN_CLOSED:

                break

        window.close()


# todo chrome option in start browser?
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
    # options.headless = True
    driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')  # create instance of browser
    return driver


def start_download(driver, artist, user, password):
    # navigate to site, go to artist page, then filter out text tabs
    driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
    driver.find_element(By.LINK_TEXT, artist).click()
    driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
    login(driver, user, password)
    print('Starting downloads...')
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
            print('Downloads finished.')
            driver.close()
            break


def login(driver, user, password):
    driver.find_element(By.CSS_SELECTOR, '.exTWY > span:nth-child(1)').click()  # login button
    time.sleep(1)
    username_textbox = driver.find_element(By.CSS_SELECTOR, '.wzvZg > div:nth-child(1) > input:nth-child(1)')
    password_textbox = driver.find_element(By.CSS_SELECTOR, '.wlfii > div:nth-child(1) > input:nth-child(1)')
    username_textbox.send_keys(user)
    password_textbox.send_keys(password)
    password_textbox.send_keys(Keys.RETURN)
    # todo deal with captcha here
    # for _ in xrange(100):  # or loop forever, but this will allow it to timeout if the user falls asleep or whatever
    #     if driver.get_current_url.find("captcha") == -1:
    #         break
    #     time.sleep(6)  # wait 6 seconds which means the user has 10 minutes before timeout occurs

    time.sleep(.5)
    # this popup sometimes takes some time to appear, wait until it's clickable
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                    'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)')))
    element.click()

    print('Logged in')
    # todo wait for captcha solved by person?
    #  Captcha help?
    # for _ in range(100):  # or loop forever, but this will allow it to timeout if the user falls asleep or whatever
    #     if driver.get_current_url.find("captcha") == -1:
    #         break
    #     time.sleep(6)  # wait 6 seconds which means the user has 10 minutes before timeout occurs

    # if driver.find_element(By.CSS_SELECTOR, '.IqBxG'):
    #     sg.popup_error(title='Login Error')
    #     print('login error')
    #     return
    #     # not perfect


def validate(artist, user, password):
    if not len(artist):
        sg.popup_error('Artist cannot be blank.')
        return False
    if not len(user):
        sg.popup_error('Username cannot be blank.')
        return False
    if not len(password):
        sg.popup_error('Password cannot be blank.')
        return False
    return True
