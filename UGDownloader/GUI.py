import time
from pathlib import Path
import PySimpleGUI as sg
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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

        # start layout
        left_column = [
            [sg.Text(text='Artist', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-ARTIST-")],
            [sg.Text(text='Username', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-USERNAME-"),
             sg.Button(button_text='Autofill'), sg.Checkbox('Run in background', default=True, key="-HEADLESS-")],
            [sg.Text(text='Password', size=(10, 1)), sg.Input(size=(25, 1), pad=(0, 10), key="-PASSWORD-"),
             sg.Button(button_text='Download'), sg.Combo(values=('Firefox', 'Chrome'), default_value='Firefox',
                                                         key="-BROWSER-")],
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
            [sg.Text(size=(30, 5), justification='center', text='-You will need Chrome or firefox installed, select '
                                                                'which one you have.')],
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
                headless = values['-HEADLESS-']
                which_browser = values['-BROWSER-']
                driver = start_browser(artist, headless, which_browser)
                try:
                    start_download(driver, artist, user, password)
                    driver.close()
                    sg.popup('Downloads finished.')
                except Exception as e:
                    print(e)
                    driver.close()
                    sg.popup_error("Something went wrong with the download. Try again- check that the "
                                   "artist you entered is on the site, and has guitar pro tabs available.")

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

        window.close()


def start_browser(artist, headless, which_browser):
    # find path of Tabs folder, and set browser options
    dl_path = str(Path.cwd())
    dl_path += '\\Tabs\\'
    dl_path += artist
    DLoader.create_artist_folder(dl_path)
    # setup browser options

    ff_options = FFOptions()
    ff_options.set_preference("browser.download.folderList", 2)
    ff_options.set_preference("browser.download.manager.showWhenStarting", False)
    ff_options.set_preference("browser.download.dir", dl_path)
    ff_options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
    ff_options.set_preference('permissions.default.stylesheet', 2)
    ff_options.set_preference('permissions.default.image', 2)
    ff_options.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')

    c_options = COptions()
    c_options.add_argument('--no-sandbox')  # not sure why this makes it work better
    preferences = {"download.default_directory": dl_path,  # pass the variable
                   "download.prompt_for_download": False,
                   "directory_upgrade": True,
                   # optimizations
                   "profile.managed_default_content_settings.images": 2,
                   "profile.default_content_setting_values.notifications": 2,
                   "profile.managed_default_content_settings.stylesheets": 2,
                   # "profile.managed_default_content_settings.cookies": 2,
                   # "profile.managed_default_content_settings.javascript": 1,
                   "profile.managed_default_content_settings.plugins": 2,
                   "profile.managed_default_content_settings.popups": 2,
                   "profile.managed_default_content_settings.geolocation": 2,
                   "profile.managed_default_content_settings.media_stream": 2}
    c_options.add_experimental_option('prefs', preferences)

    if headless:
        ff_options.headless = True
        c_options.headless = True
    if which_browser == 'Firefox':
        driver = webdriver.Firefox(options=ff_options,
                                   service=FirefoxService(GeckoDriverManager(path='Driver').install()))
    # driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')  # if I want to include local
    # driver
    if which_browser == 'Chrome':
        # driver = webdriver.Chrome(options=c_options, executable_path='chromedriver.exe')
        driver = webdriver.Chrome(options=c_options,
                                  service=ChromeService(ChromeDriverManager(path='Driver').install()))
    driver.which_browser = which_browser
    return driver


def start_download(driver, artist, user, password):
    # create log of download attempt
    failurelog = open('failurelog.txt', 'a')
    failurelog.write('\n')
    failurelog.write('Download attempt at:' + str(datetime.datetime.now()))
    failurelog.write('\n')
    failurelog.close()
    # navigate to site, go to artist page, then filter out text tabs
    driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
    driver.set_window_size(1100, 1000)
    driver.find_element(By.LINK_TEXT, artist).click()
    driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
    login(driver, user, password)
    print('Starting downloads...')
    current_page = driver.current_url
    download_count = 0
    failure_count = 0
    while True:
        results = DLoader.get_tabs(driver)
        download_count += results[0]
        failure_count += results[1]
        driver.get(current_page)
        if driver.find_elements(By.CLASS_NAME, 'BvSfz'):
            print("There's another page")
            driver.find_element(By.CLASS_NAME, 'BvSfz').click()
            current_page = driver.current_url
            continue
        else:
            # todo end message here
            print('Downloads Finished. Total number of downloads: ' + str(
                download_count) + '.')  # todo move this out of this method
            print('Total number of failures: ' + str(failure_count))
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
    # captcha css selectors
    # #captchak8gPWM_TLJs0GssOrg0gG > div:nth-child(1) > div:nth-child(1) > iframe:nth-child(1)
    # title="reCAPTCHA"
    # todo convert this java code
    # WebDriverWait(driver, 10).until(ExpectedConditions.frameToBeAvailableAndSwitchToIt(
    #     By.xpath("//iframe[starts-with(@name, 'a-') and starts-with(@src, 'https://www.google.com/recaptcha')]")));
    #
    # WebDriverWait(driver, 20).until(
    #     ExpectedConditions.elementToBeClickable(By.cssSelector("div.recaptcha-checkbox-checkmark"))).click();

    # for _ in range(100):  # or loop forever, but this will allow it to timeout if the user falls asleep or whatever
    #     if driver.get_current_url.find("captcha") == -1:
    #         break
    #     time.sleep(6)  # wait 6 seconds which means the user has 10 minutes before timeout occurs

    # todo another possible method:
    # WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[src^='https://www.google.com/recaptcha/api2/anchor?']")))
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "span.recaptcha-checkbox.goog-inline-block.recaptcha-checkbox-unchecked.rc-anchor-checkbox"))).click()
    # driver.switch_to_default_content()
    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.block.full-width.m-b"))).click()
    # time.sleep(.5)
    # this popup sometimes takes some time to appear, wait until it's clickable
    element = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,
                                    'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)')))
    element.click()

    print('Logged in')


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
