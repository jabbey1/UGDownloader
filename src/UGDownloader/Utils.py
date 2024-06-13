import logging
import subprocess
import webbrowser

from selenium.common.exceptions import NoSuchElementException, TimeoutException
import sys
from datetime import datetime
from os import mkdir
import os
from pathlib import Path
from time import sleep
from selenium.webdriver.support import expected_conditions as ec
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from packaging import version
import configparser
import re
import pathlib

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

def read_config(file_path='_UGDownloaderFiles/config.ini'):
    # current_dir = Path(__file__).resolve().parent
    # file_path = current_dir / file_path
    config = configparser.ConfigParser()
    # config.read(file_path)

    file_path = os.path.join(application_path, '_UGDownloaderFiles', 'config.ini')
    config.read(file_path)

    print("Config Location:")
    print(file_path)
    return config


# Load configuration from .ini
config = read_config()

CURRENT_VERSION = config.get('Version', 'version')
tab_download_path = config.get('Paths', 'tab_download_path', fallback=Path.cwd() / 'Tabs')
program_data_path = Path(config.get('Paths', 'program_data_path'))
userinfo_path = Path(program_data_path / 'userinfo.txt')
todownload_txt_path = Path(program_data_path / 'todownload.csv')
config_path = Path(program_data_path / 'config.ini')
log_path = Path(program_data_path / 'myapp.log')
github_api_url = config.get('Urls', 'github_api_url')
github_releases = config.get('Urls', 'github_releases')
search_url = config.get('Urls', 'search_url')
my_tabs_url = config.get('Urls', 'my_tabs_url')
LOGIN_BUTTON_SELECTOR = config.get('Selectors', 'LOGIN_BUTTON_SELECTOR')
LOGIN_FORM_SELECTOR = config.get('Selectors', 'LOGIN_FORM_SELECTOR')
LOGIN_USERNAME_SELECTOR = config.get('Selectors', 'LOGIN_USERNAME_SELECTOR')
LOGIN_PASSWORD_SELECTOR = config.get('Selectors', 'LOGIN_PASSWORD_SELECTOR')
LOGIN_SUBMIT_SELECTOR = config.get('Selectors', 'LOGIN_SUBMIT_SELECTOR')
LOGIN_POPUP_SELECTOR = config.get('Selectors', 'LOGIN_POPUP_SELECTOR')


def write_config_to_file(config: configparser.ConfigParser):
    with open(config_path, 'w') as configfile:
        config.write(configfile)
    # todo test


def open_download_folder():
    """Opens user's tab download folder in explorer."""
    try:
        subprocess.Popen(['explorer', tab_download_path])
    except Exception as e:
        print(f'Error: {e}')


def check_update():
    """Checks GitHub for updates and provides user-friendly notification."""

    try:
        response = requests.get(github_api_url)
        response.raise_for_status()  # Raise an exception if the request failed
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to GitHub: {e}")
        return

    releases = response.json()

    if not releases:
        print("No releases found on GitHub.")
        return

    latest_release = releases[0]
    latest_version = latest_release["tag_name"]

    if version.parse(latest_version) > version.parse(CURRENT_VERSION):
        print(f"\n** New version available! **")
        print(f"Upgrade to v{latest_version}:")
        print(f"Release: {latest_release['html_url']}")

        # user_input = input("Do you want to open the release page? (y/n): ")
        # if user_input.lower() == "y":
        #     webbrowser.open(latest_release['html_url'])
    else:
        print(f"You're up to date with version {CURRENT_VERSION}")






def fetch_resource(resource_path: Path) -> Path:
    """Grabs resource from local path when running as a script, grabs from a temp directory when running
        as a pyinstaller .exe. Keeps hardcoded relative paths intact. Use with pyinstaller '--add-data' command
        to add data files."""
    try:  # running as *.exe; fetch resource from temp directory
        base_path = Path(sys._MEIPASS)  # type: ignore
    except AttributeError:  # running as script; return unmodified path
        return resource_path
    else:  # return temp resource pathIn python
        return base_path.joinpath(resource_path)


def folder_check():
    """Checks for and creates the necessary files and directories."""
    if not tab_download_path.is_dir():
        mkdir(tab_download_path)
    if not program_data_path.is_dir():
        mkdir(program_data_path)
    if not userinfo_path.is_file():
        with open(userinfo_path, 'x'):
            pass
    if not todownload_txt_path.is_file():
        with open(todownload_txt_path, 'x'):
            pass
    if not log_path.is_file():
        with open(log_path, 'x'):
            pass


def login(driver, user: str, password: str, bypass_popup: bool):
    """logs in, but will be defeated if a captcha is present. Must be used when the driver is on
    a page where a login button exists. If you aren't already logged in, this will be most pages"""

    try:
        # Click on login button
        driver.find_element(By.CSS_SELECTOR, LOGIN_BUTTON_SELECTOR).click()

        # Wait for form to be present
        form = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.CSS_SELECTOR, LOGIN_FORM_SELECTOR)))
        # Find login elements
        username_textbox = form.find_element(By.CSS_SELECTOR, LOGIN_USERNAME_SELECTOR)
        password_textbox = form.find_element(By.CSS_SELECTOR, LOGIN_PASSWORD_SELECTOR)
        submit_button = form.find_element(By.CSS_SELECTOR, LOGIN_SUBMIT_SELECTOR)

        # Enter username and password
        username_textbox.send_keys(user)
        password_textbox.send_keys(password)
        sleep(1)
        submit_button.click()
        sleep(2)

        # Wait for popup to be clickable
        if bypass_popup:
            try:
                popup_element = WebDriverWait(driver, 5).until(
                    ec.element_to_be_clickable((By.CSS_SELECTOR, LOGIN_POPUP_SELECTOR)))
                popup_element.click()

            except TimeoutException:
                print('Try disabling "Bypass popup"')
        sleep(1)
        print('Logged in')

    except NoSuchElementException:
        print('Error: Could not find one of the login elements.')


def failure_log_new_attempt():
    logging.info(f"Download attempt at: {str(datetime.now())}")


def failure_log_failed_attempt(text: str):
    """This puts the url's of failed downloads in the failure log, so you could potentially go back and manually
    download files missed by the program."""
    logging.error('Failed download:' + text)

def extract_data_preserve_whitespace(line):
    # Regular expression to find and replace HTML tags
    pattern = r'<[^>]+>'
    cleaned_line = re.sub(pattern, '', line)
    return cleaned_line

def process_tab_string(tab_text_raw):
    # Splitting the input string into lines
    lines = tab_text_raw.split('\n')

    # Processing each line and storing the results
    processed_lines = [extract_data_preserve_whitespace(line) for line in lines]

    # Joining the processed lines back into a single string
    return '\n'.join(processed_lines)

def write_to_file(data, filename):
    filename_str = str(filename)
    # print('writing ' + filename_str)
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(data)

def sanitize_filename(filename):
    # Convert Path object to string if necessary
    if isinstance(filename, pathlib.Path):
        filename = str(filename)
    # Remove invalid characters
    return re.sub(r'[<>:"/\\|?*]', '', filename)

def sanitize_directory(directory):
    # Split the directory into parts
    parts = pathlib.Path(directory).parts

    # Sanitize each part of the directory
    sanitized_parts = [re.sub(r'[<>:"|?*]', '', part) for part in parts]

    # Reconstruct the path from sanitized parts
    sanitized_path = pathlib.Path(*sanitized_parts)

    return sanitized_path