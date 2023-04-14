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

# todo captcha
# todo progress bar, now easier since grabbing list of tabs all at once
# todo grab powertabs too?

# low priority:
# save text tabs as .txt files??
# progress bar, example in psgdemos all elements demo. now possible
# rewrite scroll_to_bottom without waits, as possible optimization

# pyinstaller command:
# pyinstaller --clean -F --noconsole main.py
