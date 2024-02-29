import os
import signal
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from subprocess import CREATE_NO_WINDOW
import psutil
import DLoader
import Utils


def start_browser(artist: str, headless: bool, which_browser: str, no_cookies: bool) -> (webdriver, int):
    """Builds the driver objects, depending on the browser selected. Provides driver with the download path,
    and options tailored to each browser. Sets the path of and installs the relevant driver."""
    dl_path = DLoader.create_artist_folder(artist)
    if which_browser == 'Firefox':
        firefox_options = set_firefox_options(str(dl_path), headless, no_cookies)
        print('Starting Firefox. Downloading Geckodriver.\n')
        firefox_service = FirefoxService()
        firefox_service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Firefox(options=firefox_options, service=firefox_service)

    else:
        chrome_options = set_chrome_options(str(dl_path), headless, no_cookies)
        print('Starting Chrome. Downloading Chromedriver.\n')
        chrome_service = ChromeService()
        chrome_service.creation_flags = CREATE_NO_WINDOW
        driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    driver.which_browser = which_browser
    return driver


def quit_browser(driver: webdriver):
    pid = driver.service.process.pid
    print(pid)
    process = psutil.Process(pid)
    driver.quit()
    try:
        print('aayyyy')
        os.kill(int(pid), signal.SIGTERM)
    except ProcessLookupError as ex:
        pass


def set_firefox_options(dl_path: str, headless: bool, no_cookies: bool) -> FirefoxOptions:
    """Configure the firefox driver. Sets the download directory, and browser options including headless mode. No
    cookies pop-up workaround for firefox at this point"""
    firefox_options = FirefoxOptions()
    preferences = {
        "browser.download.folderList": 2,
        "browser.download.manager.showWhenStarting": False,
        "browser.download.dir": dl_path,
        "browser.helperApps.neverAsk.saveToDisk": "application/x-gzip",
        "permissions.default.stylesheet": 2,
        "permissions.default.image": 2,
        "dom.ipc.plugins.enabled.libflashplayer.so": 'false'
    }

    for key, value in preferences.items():
        firefox_options.set_preference(key, value)

    if no_cookies:
        print('Currently, no cookies pop-up removing add-on is included for Firefox, please try Chrome instead if you '
              'are having cookies pop-up problems.\n')
    if headless:
        # firefox_options.headless = True
        firefox_options.add_argument("-headless")

    return firefox_options


def set_chrome_options(dl_path: str, headless: bool, no_cookies: bool) -> ChromeOptions:
    """Configure the Chrome Browser. Sets the download path, headless mode, and adds the 'I don't Care About Cookies'
    extension if desired."""
    chrome_options = ChromeOptions()
    # chrome_options.enable_downloads = True
    # todo is this causing zombies??
    # chrome_options.add_argument('--no-sandbox')
    preferences = {"download.default_directory": dl_path,  # give chrome download path
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
    if no_cookies:
        extension_path = Path(Utils.program_data_path / 'extension_3_4_6_0.crx')
        chrome_options.add_extension(str(Utils.fetch_resource(extension_path)))
    if headless:
        chrome_options.add_argument("--headless=new")

    return chrome_options
