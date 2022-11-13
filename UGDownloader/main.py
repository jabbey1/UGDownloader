import GUI

# testing
# artist = 'Wormrot'
# # account 1
# user = 'mygoodusername'
# password = 'passyword'
# headless = True
# which_browser = 'Chrome'
# driver = GUI.start_browser(artist, headless, which_browser)
# print(driver.which_browser)
# GUI.start_download(driver, artist, user, password)
userinfo = open('userinfo.txt', 'a')
gui = GUI.GUI()

print('fin')
# todo captcha
# todo autofill button throwing error when hasn't been used yet

# low priority:
# todo total downloads/downloads finished appearing at end of page
# todo allow for redownload of failures
# todo progress bar
# todo lock window size - headless working so may not be necessary
# todo rewrite scroll_to_bottom without waits

