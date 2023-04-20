import GUI
import DLoader

# # testing code
# artist = 'Wormrot' # average case
# artist = 'SUMAC'  # just one GPro tab

# artist = 'Radiohead'  # many pages of tabs
# # account 1
# user, password, headless, which_browser = 'mygoodusername', 'passyword', True, 'Chrome'
# driver = GUI.start_browser(artist, headless, which_browser, False)
# GUI.start_download(driver, artist, user, password)
# GUI.start_download(driver, artist, user, password, GUI.window, 'Guitar Pro')


# # testing download methods
# artist = 'Mike Dawes'  # 3 hidden tabs
# user, password = 'mygoodusername', 'passyword'
# headless, which_browser, no_cookies = True, 'Firefox', False
# driver = GUI.start_browser(artist, headless, which_browser, no_cookies)
# driver.get('https://www.ultimate-guitar.com/artist/mike_dawes_139279')
# GUI.sleep(1)
# tab_links = DLoader.collect_links_guitar_pro(driver)
# print(DLoader.download_tab(driver, tab_links[1]))
# driver.quit()


gui = GUI.GUI()

# pyinstaller command:
# pyinstaller --clean -F --noconsole UGDownloader.py
