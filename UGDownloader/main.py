import GUI
# todo test headless. does window need to be a certain size? restrict resize?
# testing
artist = 'Wormrot'
# account 1
user = 'mygoodusername'
password = 'passyword'
headless = False
which_browser = 'Chrome'
driver = GUI.start_browser(artist, headless, which_browser)
GUI.start_download(driver, artist, user, password)

# gui = GUI.GUI()

print('fin')

# todo chrome switch
# todo allow for redownload of failures
# todo lock window size
# todo total downloads/downloads finished appearing at end of page
# todo write up captcha problems
# todo progress bar
# todo set window bigger for chrome
# todo set download dir for chrome
# todo see if these are helpful: https://github.com/dinuduke/Selenium-chrome-firefox-tips
