from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FFOptions
from selenium.webdriver.chrome.options import Options as COptions
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
import DLoader
import Utils


def start_browser(artist: str, headless: bool, which_browser: str, no_cookies: bool) -> webdriver:
    """Builds the driver objects, depending on the browser selected. Provides driver with the download path,
    and options tailored to each browser. Sets the path of and installs the relevant driver."""
    dl_path = DLoader.create_artist_folder(artist)
    if which_browser == 'Firefox':
        firefox_options = set_firefox_options(dl_path, headless, no_cookies)
        print(f'Starting Firefox, downloading latest Gecko driver.\n')
        firefox_service = Service(path='_UGDownloaderFiles')
        firefox_service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Firefox(options=firefox_options,
                                   service=firefox_service)
        # driver = webdriver.Firefox(options=options, executable_path='geckodriver.exe')  # get local copy of driver

    if which_browser == 'Chrome':
        chrome_options = set_chrome_options(dl_path, headless, no_cookies)
        print(f'Starting Chrome, downloading latest chromedriver.\n')
        chrome_service = Service(path='_UGDownloaderFiles')
        chrome_service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
        # next three lines allow chrome to download files while in headless mode
        driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
        params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': dl_path}}
        driver.execute("send_command", params)
    driver.which_browser = which_browser
    return driver


def set_firefox_options(dl_path: str, headless: bool, no_cookies: bool) -> FFOptions:
    """Configure the firefox driver. Sets the download directory, and browser options including headless mode. No
    cookies pop-up workaround for firefox at this point"""
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
    """Configure the Chrome Browser. Sets the download path, headless mode, and adds the 'I don't Care About Cookies'
    extension if desired."""
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
        extension_path = Path('_UGDownloaderFiles/extension_3_4_6_0.crx')
        chrome_options.add_extension(str(Utils.fetch_resource(extension_path)))
    elif headless:
        chrome_options.headless = True
    return chrome_options
