import logging
import subprocess

from selenium.common.exceptions import NoSuchElementException
import sys
from datetime import datetime
from os import path, mkdir
from pathlib import Path
from time import sleep
from selenium.webdriver.support import expected_conditions as ec
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

VERSION = 2.4
tab_download_path = Path('Tabs')
program_data_path = Path('_UGDownloaderFiles')


def open_download_folder():
    try:
        subprocess.Popen(['explorer', tab_download_path], shell=True)
    except Exception as e:
        print(f'Error: {e}')


def check_update():
    """Uses the GitHub api to check my release page, and notifies and the newest release is different."""
    # Make a request to the GitHub API to get the releases
    api_url = "https://api.github.com/repos/jabbey1/UGDownloader/releases"
    print('Checking for updated .exe release.')
    try:
        response = requests.get(api_url)
    except Exception as e:
        print(f"Error occurred while checking for update: {e}")
        return

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


def fetch_resource(resource_path: Path) -> Path:
    """Grabs resource from local path when running as a script, grabs from a temp directory when running
        as a pyinstaller .exe. Keeps hardcoded relative paths intact. Use with pyinstaller '--add-data' command
        to add data files."""
    try:  # running as *.exe; fetch resource from temp directory
        base_path = Path(sys._MEIPASS)
    except AttributeError:  # running as script; return unmodified path
        return resource_path
    else:  # return temp resource path
        return base_path.joinpath(resource_path)


def folder_check():
    # makes sure that the Tabs folder and the userinfo.txt, todownload.txt files exist
    if not path.isdir(tab_download_path):
        mkdir(tab_download_path)
    if not path.isdir(program_data_path):
        mkdir(program_data_path)
    # todo remove these hardcoded paths
    if not path.isfile('_UGDownloaderFiles/userinfo.txt'):
        with open('_UGDownloaderFiles/userinfo.txt', 'x'):
            pass
    if not path.isfile('_UGDownloaderFiles/todownload.csv'):
        with open('_UGDownloaderFiles/todownload.csv', 'x'):
            pass


def login(driver: webdriver, user: str, password: str):
    """logs in, but will be defeated if a captcha is present. Must be used when the driver is on
    a page where a login button exists. If you aren't already logged in, this will be most pages"""
    # CSS selectors
    login_button_selector = '.exTWY'
    form_selector = "form > div.PictU"
    username_selector = 'input[name=username]'
    password_selector = 'input[name=password]'
    submit_selector = 'button[type=submit]'
    popup_selector = 'button.RwBUh:nth-child(1) > svg:nth-child(1) > path:nth-child(1)'

    try:
        # Click on login button
        driver.find_element(By.CSS_SELECTOR, login_button_selector).click()

        # Wait for form to be present
        form = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.CSS_SELECTOR, form_selector)))
        # Find login elements
        username_textbox = form.find_element(By.CSS_SELECTOR, username_selector)
        password_textbox = form.find_element(By.CSS_SELECTOR, password_selector)
        submit_button = form.find_element(By.CSS_SELECTOR, submit_selector)

        # Enter username and password
        username_textbox.send_keys(user)
        password_textbox.send_keys(password)
        sleep(1)
        submit_button.click()

        # Wait for popup to be clickable
        popup_element = WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.CSS_SELECTOR, popup_selector)))
        popup_element.click()
        sleep(.5)
        print('Logged in')

    except NoSuchElementException:
        print('Error: Could not find one of the login elements.')


def failure_log_new_attempt():
    logging.info(f"Download attempt at: {str(datetime.now())}")


def failure_log_failed_attempt(text: str):
    """This puts the url's of failed downloads in the failure log, so you could potentially go back and manually
    download files missed by the program."""
    logging.error('Failed download:' + text)
