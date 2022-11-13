import GUI

# testing code
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
# todo track down firefox bug- happens before login it seems
# low priority:
# todo change or allow customization to folders
# todo total downloads/downloads finished appearing at end of page
# todo allow for redownload of failures
# todo progress bar
# todo lock window size - headless working so may not be necessary
# todo rewrite scroll_to_bottom without waits, as possible optimization
