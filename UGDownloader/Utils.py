import os
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
VERSION = 1.6


def check_update():
    """Uses the GitHub api to check my release page, and notifies and the newest release is different."""
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


def login(driver: webdriver, user: str, password: str):
    """logs in, but will be defeated if a captcha is present. Must be used when the driver is on
    a page where a login button exists. If you aren't already logged in, this will be most pages"""
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


def failure_log_new_attempt():
    with open('_UGDownloaderFiles/failurelog.txt', 'a+') as failurelog:
        failurelog.write(f"\nDownload attempt at: {str(datetime.now())}\n")
        failurelog.write(f"URLs of failed downloads:\n")


def failure_log_failed_attempt(text: str):
    """This puts the url's of failed downloads in the failure log, so you could potentially go back and manually
    download files missed by the program."""
    with open('_UGDownloaderFiles\\failurelog.txt', 'a') as failurelog:
        failurelog.write(text + '\n')

