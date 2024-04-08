import os
import sys
import threading
from time import sleep
from tkinter import ttk
import customtkinter
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
import DLoader
import DriverSetup
import Utils

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    EXITING = False
    CANCELED = False
    DOWNLOADING = False
    selected_table_item = ''
    program_data_path = Utils.program_data_path
    todl_path = Utils.todownload_txt_path
    user_info_path = Utils.userinfo_path
    os.environ['WDM_PROGRESS_BAR'] = str(0)

    def __init__(self, ):
        super().__init__()
        self.driver = None
        Utils.folder_check()
        self.resizable(False, False)
        self.title('Ultimate Guitar Downloader')
        self.geometry(f"{1200}x{900}")

        """GUI arrangement begin"""
        # configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        """left sidebar"""
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=11, sticky="nsew")
        self.sidebar_frame.rowconfigure(8, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text='UGDownloader',
                                                 font=customtkinter.CTkFont(size=20, weight='bold'))
        self.logo_label.grid(row=0, column=0, padx=20, pady=10)

        # text entry
        self.user_text_entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text='username')
        self.user_text_entry.grid(row=1, column=0, padx=20, )

        self.password_text_entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text='password', show='*')
        self.password_text_entry.grid(row=2, column=0, padx=20, pady=10, )

        # text buttons
        self.autofill_button = customtkinter.CTkButton(self.sidebar_frame, width=10, text='Autofill',
                                                       command=self.autofill_button_event)
        self.autofill_button.grid(row=3, column=0, sticky='w', padx=22)
        self.save_info_button = customtkinter.CTkButton(self.sidebar_frame, width=10, text='Save Info',
                                                        command=self.save_info_button_event)
        self.save_info_button.grid(row=3, column=0, sticky='e', padx=25)

        # segmented button browser selector
        self.browser_button = customtkinter.CTkSegmentedButton(self.sidebar_frame, values=['Chrome', 'Firefox'])
        self.browser_button.grid(row=4, column=0, padx=22, pady=10, sticky='w')

        # checkboxes
        self.headless_checkbox = customtkinter.CTkCheckBox(self.sidebar_frame, onvalue=True, offvalue=False,
                                                           text='Run in background')
        self.headless_checkbox.grid(row=5, column=0, padx=20, sticky='w')
        self.cookies_checkbox = customtkinter.CTkCheckBox(self.sidebar_frame, onvalue=True, offvalue=False,
                                                          text='Bypass Cookies (E.U.)')
        self.cookies_checkbox.grid(row=6, column=0, padx=20, pady=(10, 0), sticky='w')

        # Exiting/control buttons
        self.appearance_mode_option_menu = customtkinter.CTkOptionMenu(self.sidebar_frame,
                                                                       values=["Light", "Dark", "System"],
                                                                       command=change_appearance_mode_event)
        self.appearance_mode_option_menu.grid(row=8, column=0, sticky='s')
        self.open_folder_button = customtkinter.CTkButton(self.sidebar_frame, text='Open Tab Folder',
                                                          command=self.open_folder_button_event)
        self.open_folder_button.grid(row=9, column=0, pady=(10, 0))
        self.check_for_new_tabs_button = customtkinter.CTkButton(self.sidebar_frame, text='Check Artist Tab Count',
                                                                 command=self.check_for_new_tabs_event)
        self.check_for_new_tabs_button.grid(row=10, column=0, pady=(10, 0))
        self.cancel_button = customtkinter.CTkButton(self.sidebar_frame, text='Cancel Download',
                                                     command=self.cancel_button_event)
        self.cancel_button.grid(row=11, column=0, pady=10)
        self.exit_button = customtkinter.CTkButton(self.sidebar_frame, text='Exit', command=self.exit_button_event)
        self.exit_button.grid(row=12, column=0, pady=(0, 20))

        """Middle"""
        self.console_output = customtkinter.CTkTextbox(self, width=350, border_color='white', border_width=1,
                                                       wrap='word', )
        self.console_output.grid(row=0, column=1, rowspan=3, columnspan=2, padx=6, pady=10, sticky='nsew')
        self.progress_bar = customtkinter.CTkProgressBar(self, mode='determinate')
        self.progress_bar.grid(row=9, column=1, padx=20, pady=10, columnspan=2, sticky='ew')

        """right bar"""
        self.right_frame = customtkinter.CTkFrame(self, )
        self.right_frame.grid(row=0, column=3, sticky='nsew', columnspan=2, rowspan=10, padx=6, pady=10)
        self.right_frame.grid_columnconfigure(1, weight=1)
        self.right_frame.grid_rowconfigure(3, weight=1)

        # to download section
        self.add_artist_button = customtkinter.CTkButton(self.right_frame, width=10, text='Add',
                                                         command=self.add_artist_button_event)
        self.add_artist_button.grid(row=0, column=0, padx=10, pady=10, sticky='w')
        self.todl_artist_entry = customtkinter.CTkEntry(self.right_frame, width=10, )
        self.todl_artist_entry.grid(row=0, column=0, sticky='ew', padx=(55, 10), columnspan=2)

        columns = '1'
        self.todl_table = ttk.Treeview(self.right_frame, columns=columns, height=7, selectmode='browse',
                                       show='headings')

        self.todl_table.column("#1", anchor="c", minwidth=50, width=50)
        self.todl_table.heading('1', text='Artists to download')
        self.scrollbar = customtkinter.CTkScrollbar(self.right_frame, orientation='vertical',
                                                    command=self.todl_table.yview)
        self.todl_table.configure(yscrollcommand=self.scrollbar.set)
        self.todl_table.grid(row=1, column=0, sticky='nsew', padx=10, pady=10)
        self.scrollbar.grid(row=1, column=1, sticky='nse', pady=5)

        self.get_todl_data()

        self.selected_table_item = self.todl_table.selection()
        self.todl_table.grid(row=1, column=0, padx=10, columnspan=2, rowspan=1, sticky='news')
        # table styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=25,
                        fieldbackground="#343638",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#22559b')])
        style.configure("Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat")
        style.map("Treeview.Heading", background=[('active', '#3484F0')])
        # table buttons
        self.copy_button = customtkinter.CTkButton(self.right_frame, width=130, text='Copy',
                                                   command=self.copy_button_event)
        self.copy_button.grid(row=2, column=0, sticky='w', padx=10, pady=10, columnspan=2)
        self.delete_button = customtkinter.CTkButton(self.right_frame, width=130, text='Delete',
                                                     command=self.delete_button_event)
        self.delete_button.grid(row=2, column=1, sticky='e', padx=10)

        # Notes/instructions/troubleshooting
        self.information_tabview = customtkinter.CTkTabview(self.right_frame, width=200)
        self.information_tabview.grid(row=3, column=0, columnspan=2, padx=10, pady=(0, 10), sticky='nsew')
        # add tabs to tabview
        self.information_tabview.add('Notes')
        self.information_tabview.add('2')
        self.information_tabview.add('3')
        # Configure tab layouts
        self.information_tabview.tab('Notes').grid_columnconfigure(0, weight=1)
        self.information_tabview.tab('Notes').grid_rowconfigure(0, weight=1)
        self.information_tabview.tab('2').grid_columnconfigure(0, weight=1)
        self.information_tabview.tab('2').grid_rowconfigure(0, weight=1)
        self.information_tabview.tab('3').grid_columnconfigure(0, weight=1)
        self.information_tabview.tab('3').grid_rowconfigure(0, weight=1)
        # configure textboxes inside tabs
        self.note_1_text = customtkinter.CTkTextbox(self.information_tabview.tab('Notes'), wrap='word')
        self.note_1_text.grid(row=0, column=0, sticky='nsew')
        self.note_2_text = customtkinter.CTkTextbox(self.information_tabview.tab('2'), wrap='word')
        self.note_2_text.grid(row=0, column=0, sticky='nsew')
        self.note_3_text = customtkinter.CTkTextbox(self.information_tabview.tab('3'), wrap='word')
        self.note_3_text.grid(row=0, column=0, sticky='nsew')

        """bottom"""
        self.artist_entry = customtkinter.CTkEntry(self, placeholder_text='Artist', width=300)
        self.artist_entry.grid(row=10, column=1, columnspan=1, pady=(10, 20), padx=10, sticky='e') #steve
        self.mytabs_checkbox = customtkinter.CTkCheckBox(self, onvalue=True, offvalue=False,
                                                    text='Download \"My Tabs\"')
        self.mytabs_checkbox.grid(row=10, column=2, pady=(10, 20), sticky='w') #steve
        self.filetype_drop_down = customtkinter.CTkOptionMenu(self, values=['Guitar Pro', 'Powertab', 'Text', 'All'])
        self.filetype_drop_down.grid(row=10, column=3, pady=(10, 20))
        self.download_button = customtkinter.CTkButton(self, text='Download', command=self.download_button_event)
        self.download_button.grid(row=10, column=4, pady=(10, 20), padx=10)
        self.progress_bar.set(0)

        """GUI arrangement over"""

        # set default values
        self.browser_button.set('Chrome')
        self.headless_checkbox.select()
        self.filetype_drop_down.set('Text')
        self.appearance_mode_option_menu.set('Dark')
        self.information_tabview.set('Notes')
        # Set notes
        self.note_1_text.insert('0.0', "-Ultimate Guitar requires a login to download tabs. If you just created an "
                                       "account, you may have to wait a day or two for the captcha to stop appearing "
                                       "(this program won't work while that's appearing)."
                                       "\n\n-You will need Chrome or firefox installed, select which one you have.")
        self.note_2_text.insert('0.0', "-Artist entered must be an exact, case sensitive match to what Ultimate "
                                       "Guitar has listed."
                                       "\n\n-Tabs will be downloaded to the folder this program is in."
                                       "\n\n-You can edit the 'to download' list manually, it is located in the "
                                       "_UGDownloaderFiles folder.")
        self.note_3_text.insert('0.0', "-Bypass Cookies uses the I don't care about cookies add-on, and will only "
                                       "work using Chrome and will not run in the background.")
        # Redirect console output
        sys.stdout = StdoutRedirector(self.console_output)
        Utils.check_update()
        self.autofill_button_event(True)

    """GUI button events"""

    @staticmethod
    def open_folder_button_event():
        print('Opening "Tabs" folder.')
        Utils.open_download_folder()

    def check_for_new_tabs_event(self):
        """Takes the entered artist and runs the new tabs checker, which counts the number of tabs you already have from
        an artist, and how many are online, and reports back without downloading any. Creates driver instance"""
        print('\nPlease wait...\n')

        my_tabs_requested = bool(self.mytabs_checkbox.get())

        artist = ''
        if not my_tabs_requested:
            artist = self.artist_entry.get()
            if not validate(artist, 'user', 'password', my_tabs_requested):
                return

        headless, browser, cookies, filetype = bool(self.headless_checkbox.get()), self.browser_button.get(), \
            bool(self.cookies_checkbox.get()), self.filetype_drop_down.get()

        driver = DriverSetup.start_browser(artist, headless, browser, cookies)
        try:
            thread = threading.Thread(target=lambda: DLoader.new_tabs_checker(driver, artist, filetype, my_tabs_requested))
            thread.start()

        except Exception as e:
            print(f'Error: {e}')
            print('Finding tab count failed.')
            print('Closing browser...')
            driver.quit()
            print('Browser closed.')

    def copy_button_event(self):
        """Copies selection from to download table into the artist text entry """
        if not self.todl_table.selection():
            print('Nothing selected')
            return

        selected_item = self.todl_table.focus()
        item_text = self.todl_table.item(selected_item)['values'][0]

        self.artist_entry.delete(0, 'end')
        self.artist_entry.insert(0, item_text)

    def delete_button_event(self):
        """Gets the selected value to delete from the table in the window, and then rewrites text file to reflect
        change."""

        if not self.todl_table.selection():
            print('Nothing selected')
            return

        selected_item = self.todl_table.focus()
        item_text = self.todl_table.item(selected_item)['values'][0]
        print(f'Removed {item_text} from to download list.')
        with open(self.todl_path, 'r') as file:
            content = file.readline()
            items = content.split(',')
        with open(self.todl_path, 'w') as file:
            for item in items:
                if item != item_text and item != "":
                    new_entry = item + ','
                    file.write(new_entry)
        self.get_todl_data()

    def add_artist_button_event(self):
        """adds new artist to the to download list text file, and then updates the table."""
        new_artist = self.todl_artist_entry.get()
        if not new_artist:
            print('No artist to add. Please type one in the input box.')
            return
        new_entry = ',' + new_artist.strip()
        with open(self.todl_path, 'a') as file:
            file.write(new_entry)
        self.get_todl_data()
        print(f'New artist added to download list: {new_artist.strip()}')

    def autofill_button_event(self, startup=None):
        """Update the user and password text fields with user's data from text file, if it exists and is valid."""
        with open(self.user_info_path, 'r') as userinfo:
            data = []
            for line in userinfo:
                data = line.split()
            if len(data) == 2:
                self.user_text_entry.delete(0, 'end')
                self.password_text_entry.delete(0, 'end')
                self.user_text_entry.insert(0, data[0])
                self.password_text_entry.insert(0, data[1])
            elif startup is None:
                print('There is either no user info saved or the data saved is invalid.')

    def save_info_button_event(self):
        """Saves username and password to .txt file"""
        user, password = self.user_text_entry.get(), self.password_text_entry.get()
        if not validate('A', user, password, False):
            return  # faked artist field to not trip validate
        with open(self.user_info_path, 'w+') as userinfo:
            userinfo.write(f'{user} {password}')
        print('New User info saved.')

    def download_button_event(self):
        """Collect all information from the text fields to send to a new thread. Prevents downloading if a download
        is already in progress. Driver quits if the thread fails, otherwise driver must be quit inside the
        download method"""

        if self.DOWNLOADING:
            print("Download already in progress. Please wait.")
            return

        # pull options from GUI fields

        artist, user, password, my_tabs_requested = self.artist_entry.get(), self.user_text_entry.get(), \
            self.password_text_entry.get(), bool(self.mytabs_checkbox.get())
        headless, browser, cookies, filetype = bool(self.headless_checkbox.get()), self.browser_button.get(), \
            bool(self.cookies_checkbox.get()), self.filetype_drop_down.get()

        if not validate(artist, user, password, my_tabs_requested):
            return

        # set download state and prepare progress bar
        self.DOWNLOADING = True
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        driver = DriverSetup.start_browser(artist, headless, browser, cookies)
        count = DLoader.get_already_downloaded_count(artist)

        if not my_tabs_requested:
            print(f'There are {count} files in the "{artist}" directory.\n')

        try:
            thread = threading.Thread(target=lambda: start_download(driver, artist, user, password, self, filetype))
            thread.start()
        except Exception as e:
            self.DOWNLOADING = False
            print('Something went wrong with starting the download. Error:')
            print(e)
            print('Closing browser...')
            driver.quit()
            print('Browser closed.')

    def cancel_button_event(self):
        """Cancels current download. Has to wait for the download thread to notice the new state."""
        if not self.DOWNLOADING:
            print('No download to cancel')
            return
        print('Canceling...')
        self.CANCELED = True

    def exit_button_event(self):
        print('Exiting.')
        self.EXITING = True
        self.exit_program()

    def on_close(self):
        print('Exiting.')
        self.EXITING = True
        self.exit_program()

    def get_todl_data(self):
        """updates 'to download data' from the text file, updates table with new data"""
        with open(self.todl_path, 'r') as file:
            content = file.readline()
            todl_data = content.split(',')
        self.todl_table.delete(*self.todl_table.get_children())
        for item in todl_data:
            if item != '':
                self.todl_table.insert('', 'end', values=(f'{item}',))

    def exit_program(self):
        try:
            if driver:
                print('Closing browser...')
                driver.quit()
                print('Browser closed.')
        except Exception as e:
            print(e)
            pass
        self.destroy()
        if os.path.exists('geckodriver.log'):
            os.remove('geckodriver.log')


def validate(artist: str, user: str, password: str,
             my_tabs_requested: bool) -> bool:
    if not artist and not my_tabs_requested:
        print('Artist cannot be blank.')
        return False
    if not user:
        print('Username cannot be blank.')
        return False
    if not password:
        print('Password cannot be blank.')
        return False
    return True


def change_appearance_mode_event(new_appearance_mode: str):
    customtkinter.set_appearance_mode(new_appearance_mode)


def start_download(driver: webdriver, artist: str, user: str, password: str, gui: App, file_type_wanted: str):
    """Set up the failure log, and then plug the desired artist into UG's search function. Artists have an id
    associated with them, so you can't navigate directly to their page with only their name. Searching and then
    attempting to click on the artists name on the page will get you to the artists page or let you know if you've
    made a mistake with typing the artist's name. Once at the artist's page, you can collect links to all the files
    that you want to download. Once the actual download process begins, interruptions are allowed. Retrying failed
    attempts are handled in this method, as well as tracking failures, successes, and reporting overall progress"""
    Utils.failure_log_new_attempt()

    # if mytabs checked
    search_url = Utils.search_url
    if bool(gui.mytabs_checkbox.get()):
        try:
            search_url = search_url + "Wilco" # force a login popup
            driver.get(search_url)
            # setting the window size seems to help some element obfuscation issues
            driver.set_window_size(1100, 1200)
            # click on artist from search results        
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print("Cannot find My Tabs. Do you have any saved tabs?\n")
            gui.DOWNLOADING = False
            gui.progress_bar.stop()
            print('Closing browser...')
            driver.quit()
            print('Browser closed.')
            return
    else:
        try:
            driver.get(search_url + artist)
            # setting the window size seems to help some element obfuscation issues
            driver.set_window_size(1100, 1000)
            # click on artist from search results        
            driver.find_element(By.LINK_TEXT, artist).click()
        except (TypeError, selenium.common.exceptions.NoSuchElementException):
            print("Cannot find artist. Did you type it in with the exact spelling and capitalization?\n")
            gui.DOWNLOADING = False
            gui.progress_bar.stop()
            print('Closing browser...')
            driver.quit()
            print('Browser closed.')
            return
    if driver.which_browser == 'Firefox':
        sleep(1)

    print('Logging in...')
    Utils.login(driver, user, password)
    download_count, failure_count, tab_links = 0, 0, {'download': [], 'text': []}

    # because trying to visit 'my tabs' when logged out brings you to the forums
    if bool(gui.mytabs_checkbox.get()):
        print('Navigating to My Tabs...')
        driver.get(Utils.my_tabs_url)

    if check_canceled(gui):
        return
    print('Grabbing urls of requested files.\n')
    tab_links = DLoader.link_handler(driver, tab_links,
                                     file_type_wanted,
                                     bool(gui.mytabs_checkbox.get()),
                                     artist)
    total_tabs = (len(tab_links['download'])+len(tab_links['text']))

    print(f'Attempting {total_tabs} downloads.')
    gui.progress_bar.stop()
    gui.progress_bar.set(0)
    gui.progress_bar.configure(mode="determinate")
    gui.progress_bar["maximum"] = total_tabs
    tabs_attempted = 0
    driver.wait_on_first_tab = True
    for link in tab_links['download']:
        # download interruptions
        if check_exiting(gui):
            return
        if check_canceled(gui):
            break

        results = DLoader.download_tab(driver, link)
        # try again after failure, 3 tries. Results[0] == 1 means a download was made
        tries = 1
        while results[0] == 0 and tries < 2:
            tries += 1
            print(f'Download failed, trying again. Attempt {tries}')
            attempt_results = DLoader.download_tab(driver, link)
            results[0] += attempt_results[0]
            results[1] += attempt_results[1]
        if tries >= 3:
            Utils.failure_log_failed_attempt(link)
            print('Too many download attempts. Moving on')
        tabs_attempted += 1
        download_count += results[0]
        failure_count += results[1]
        gui.progress_bar.set(tabs_attempted / 
                             total_tabs)

    for info in tab_links['text']:
        # download interruptions
        if check_exiting(gui):
            return
        if check_canceled(gui):
            break

        # grab the artist and song title from the link
        # TODO @steveandroulakis grab the artist and song title from the page
        # and work to ensure uniqueness (across tab versions)
        print(info) #steve
        if 'artist' in info and info['artist'] != '':
            artist = info['artist']
            DLoader.create_artist_folder(artist)

        title = info['title']
        type = info['type']
        link = info['link']
        artist_title_type = f'{artist} - {title} - {type}'

        filename = f'{artist_title_type}.txt'
        fullpath = Utils.tab_download_path / artist
        filename_fullpath = fullpath / filename

        print(f'\n{artist_title_type}')

        # if filename_fullpath exists, skip
        # TODO @steveandroulakis count skipped files
        if filename_fullpath.is_file():
            print(f'File already exists. Skipping.\n')
        else:
            tab_text_raw = DLoader.download_text(driver, link)
            #print(tab_text_raw)

            tab_text = Utils.process_tab_string(tab_text_raw)

            # prepend artist_title to tab_text
            tab_text = artist_title_type + '\n\n' + tab_text
            print(f'Writing to file: {filename_fullpath} \n')
            Utils.write_to_file(tab_text,
                                Utils.sanitize_filename(filename_fullpath))

        tabs_attempted += 1
        download_count += 1
        failure_count += 0 # TODO @steveandroulakis failure attempts for text
        gui.progress_bar.set(tabs_attempted /
                             total_tabs)

    # A wait here allows the browser to finish downloads before being closed.
    sleep(2)
    print('Downloads Finished.')
    print(f'Total number of downloads: {str(download_count)}.')
    print(f'Total number of failures: {str(failure_count)}')
    print('Closing browser...')
    driver.quit()
    print('Browser closed.')
    gui.DOWNLOADING = False


def check_exiting(gui: App):
    if gui.EXITING:
        gui.DOWNLOADING = False
        print('Closing browser...')
        driver.quit()
        print('Browser closed.')
        return True
    return False


def check_canceled(gui: App):
    if gui.CANCELED:
        gui.CANCELED = False
        print('Download canceled.')
        gui.DOWNLOADING = False
        return True
    return False


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.console_output = text_widget

    def write(self, string):
        self.console_output.configure(state='normal')
        self.console_output.insert('end', string)
        self.console_output.see('end')
        self.console_output.configure(state='disabled')

    def flush(self):
        self.console_output.update_idletasks()


if __name__ == "__main__":
    app = App()
    app.mainloop()
