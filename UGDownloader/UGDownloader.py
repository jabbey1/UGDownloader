import GUI

# # testing code
# artist = 'Wormrot' # average case
# artist = 'SUMAC'  # just one GPro tab
# artist = 'Radiohead'  # many pages of tabs
# # account 1
# user, password, headless, which_browser = 'mygoodusername', 'passyword', True, 'Chrome'
# driver = GUI.start_browser(artist, headless, which_browser)
# GUI.start_download(driver, artist, user, password)

gui = GUI.GUI()

# pyinstaller command:
# pyinstaller --clean -F --noconsole UGDownloader.py