from time import sleep
import PySimpleGUI as sG
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
import Utils
import DLoader
import DriverSetup

THREAD_KEY = '-THREAD-'
DL_START_KEY = '-START DOWNLOAD-'
DL_COUNT_KEY = '-COUNT-'
DL_END_KEY = '-END DOWNLOAD-'
DL_THREAD_EXITING = '-THREAD EXITING-'


class GUI:
    EXITING = False
    CANCELED = False

    def __init__(self):
        Utils.folder_check()
        todl_data = get_todl_data()

        # start layout
        left_column = [
            [sG.Text(text='Artist', size=(10, 1)), sG.Input(size=(25, 1), pad=(0, 10), key="-ARTIST-"),
             sG.Button(button_text='Save Info'),
             sG.Checkbox('Bypass cookies (E.U.), Chrome', default=False, key="-COOKIES-")],
            [sG.Text(text='Username', size=(10, 1)), sG.Input(size=(25, 1), pad=(0, 10), key="-USERNAME-"),
             sG.Button(button_text='Autofill'), sG.Checkbox('Run in background', default=True, key="-HEADLESS-")],
            [sG.Text(text='Password', size=(10, 1)), sG.Input(size=(25, 1), pad=(0, 10), key="-PASSWORD-"),
             sG.Button(button_text='Download'),
             sG.Combo(values=('Guitar Pro', 'Powertab', 'Both'), default_value='Guitar Pro', key="-FILETYPE-"),
             sG.Combo(values=('Chrome', 'Firefox'), default_value='Chrome', key="-BROWSER-")],
            [sG.Text(text='Progress'), sG.ProgressBar(100, 'h', size=(30, 20), key='-PROGRESS-', expand_x=True)],
            [sG.HSeparator()],
            [sG.Multiline(size=(60, 11), font='Courier 8', expand_x=True, expand_y=True,
                          write_only=True, reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True,
                          autoscroll=True, auto_refresh=True)],
            [sG.HSeparator()],
            [sG.Button(button_text='Copy Artist Name'), sG.Button(button_text='Add'), sG.Button(button_text='Delete'),
             sG.Input(size=(35, 1), pad=(0, 10), key="-TODLINPUT-")],
            [sG.Table(values=todl_data[:], num_rows=9, headings=['Artists to Download'],
                      key="-TODLTABLE-", enable_events=True, justification='center', expand_x=True)]

        ]

        right_column = [
            [sG.Text(size=(30, 4), justification='left',
                     text="-Artist entered must be an exact, case sensitive match to what Ultimate "
                          "Guitar has listed.")],
            [sG.Text(size=(30, 4), justification='left',
                     text="-Files will be downloaded to the folder this program is in.")],
            [sG.Text(size=(30, 4), justification='left', text='-You will need Chrome or firefox installed, select '
                                                              'which one you have.')],
            [sG.Text(size=(30, 6), justification='left',
                     text="-Ultimate Guitar requires a login to download tabs. If you just created an account, "
                          "you may have to wait a day or two for the captcha to stop appearing (this program won't "
                          "work while that's appearing).")],
            [sG.HSeparator(pad=((0, 0), (150, 10)))],
            [sG.Button(button_text='Cancel Download', expand_x=True)],
            [sG.Button(button_text='Exit', expand_x=True)]
        ]

        # ----- Full layout -----
        layout = [
            [
                sG.Column(left_column),
                sG.VSeperator(),
                sG.Column(right_column, vertical_alignment='top')
            ]
        ]
        # end layout

        window = sG.Window("Ultimate Guitar Downloader", layout)

        downloading = False
        window.finalize()
        Utils.check_update()

        # Run loop start
        while True:
            event, values = window.read()

            if event == "Save Info":
                save_user_info(values['-USERNAME-'], values['-PASSWORD-'])

            if event == "Autofill":
                autofill_user(window)

            if event == "Download":
                artist, user, password = values['-ARTIST-'], values['-USERNAME-'], values['-PASSWORD-']

                if downloading:
                    print("Download already in progress. Please wait.")
                    continue
                if not validate(artist, user, password):
                    continue

                downloading = True
                driver = DriverSetup.start_browser(artist, values['-HEADLESS-'],
                                                   values['-BROWSER-'], values['-COOKIES-'])
                try:
                    window.start_thread(
                        lambda: start_download(driver, artist, user, password, window, values['-FILETYPE-']),
                        (THREAD_KEY, DL_THREAD_EXITING))
                except Exception as e:
                    downloading = False
                    print(e)
                    driver.quit()
                    sG.popup_error("Something went wrong with the download. Try again- The most common problem is that"
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

            if event == "Exit" or event == sG.WIN_CLOSED:
                print('Exiting.')
                GUI.EXITING = True
                break

            # thread events
            elif event[0] == THREAD_KEY:
                if event[1] == DL_START_KEY:
                    max_value = values[event]
                    window['-PROGRESS-'].update(0, max_value)
                elif event[1] == DL_COUNT_KEY:
                    window['-PROGRESS-'].update(values[event], max_value)
                elif event[1] == DL_END_KEY:
                    downloading = False
                elif event[1] == DL_THREAD_EXITING:
                    pass
        window.close()
        # just to make sure driver has quit to prevent orphaned instances, doesn't matter if there's an exception at
        # this point
        try:
            driver.quit()
        except Exception as e:
            pass


def autofill_user(window: sG.Window):
    """Update the user and password text fields with user's data from text file, if it exists and is valid."""
    with open('_UGDownloaderFiles/userinfo.txt', 'r') as userinfo:
        data = []
        for line in userinfo:
            data = line.split()
        if len(data) == 2:
            window["-USERNAME-"].update(data[0])
            window["-PASSWORD-"].update(data[1])
        else:
            print('There is either no user info saved or the data saved is invalid.')


def start_download(driver: webdriver, artist: str, user: str, password: str, window: sG.Window, file_type_wanted: str):
    """Set up the failure log, and then plug the desired artist into UG's search function. Artists have an id
    associated with them, so you can't navigate directly to their page with only their name. Searching and then
    attempting to click on the artists name on the page will get you to the artists page or let you know if you've
    made a mistake with typing the artist's name. Once at the artist's page, you can collect links to all the files
    that you want to download. Once the actual download process begins, interruptions are allowed. Retrying failed
    attempts are handled in this method, as well as tracking failures, successes, and reporting overall progress"""
    Utils.failure_log_new_attempt()
    driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
    # setting the window size seems to help some element obfuscation issues
    driver.set_window_size(1100, 1000)
    # click on artist from search results
    try:
        driver.find_element(By.LINK_TEXT, artist).click()
    except (TypeError, selenium.common.exceptions.NoSuchElementException):
        print("Cannot find artist. Did you type it in with the exact spelling and capitalization?\n")
        return
    if driver.which_browser == 'Firefox':
        sleep(1)

    Utils.login(driver, user, password)
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
        while results[0] == 0 and tries < 4:
            tries += 1
            print(f'Download failed, trying again. Attempt {tries}')
            attempt_results = DLoader.download_tab(driver, link)
            results[0] += attempt_results[0]
            results[1] += attempt_results[1]
        if tries >= 4:
            Utils.failure_log_failed_attempt(link)
            print(f'Too many download attempts. Moving on')
        tabs_attempted += 1
        download_count += results[0]
        failure_count += results[1]
        window.write_event_value((THREAD_KEY, DL_COUNT_KEY), tabs_attempted)
    driver.quit()
    print(f'Downloads Finished. Total number of downloads: {str(download_count)}.')
    print(f'Total number of failures: {str(failure_count)}')
    window.write_event_value((THREAD_KEY, DL_END_KEY), len(tab_links))


def validate(artist: str, user: str, password: str) -> bool:
    if not artist:
        sG.popup_error('Artist cannot be blank.')
        return False
    if not user:
        sG.popup_error('Username cannot be blank.')
        return False
    if not password:
        sG.popup_error('Password cannot be blank.')
        return False
    return True


def get_todl_data() -> list:
    """updates to download data from the text file"""
    with open("_UGDownloaderFiles\\todownload.txt", 'r') as f:
        todl_data = [[line.rstrip()] for line in f]
    return todl_data


def add_to_todl_list(window: sG.Window, values: dict):
    """To add data to your to download list. Calls method to update the list, and updates the table in the window"""
    if not values['-TODLINPUT-']:
        print('No artist to add. Please type one in the input box.')
        return
    with open('_UGDownloaderFiles/todownload.txt', 'a') as file:
        file.write('\n' + values['-TODLINPUT-'])
    todl_data = get_todl_data()
    print(f'New artist added to download list: {values["-TODLINPUT-"]}')
    window['-TODLTABLE-'].update(values=todl_data[:])


def delete_from_todl(window: sG.Window, values: dict, todl_data: list):
    """Gets the selected value to delete from the table in the window, and then rewrites text file to reflect change"""
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


def copy_artist_name(window: sG.Window, values: dict, todl_data: list):
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
