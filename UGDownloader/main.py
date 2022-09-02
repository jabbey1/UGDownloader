import GUI
# todo test headless. does window need to be a certain size? restrict resize?
# testing
artist = 'Wormrot'
# account 1
user = 'mygoodusername'
password = 'passyword'
headless = False
which_browser = 'Firefox'
driver = GUI.start_browser(artist, headless, which_browser)
GUI.start_download(driver, artist, user, password)

# gui = GUI.GUI()

print('fin')

# todo lock window size
# todo set window bigger for chrome
# todo make sure chrome can finish downloads before closing
# todo test headless chrome

# low priority:
# todo write up captcha problems
# todo total downloads/downloads finished appearing at end of page
# todo allow for redownload of failures
# todo progress bar

