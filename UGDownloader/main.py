import GUI

# # testing code
# artist = 'Wormrot'
# # account 1
# user = 'mygoodusername'
# password = 'passyword'
# headless = True
# which_browser = 'Chrome'
# driver = GUI.start_browser(artist, headless, which_browser)
# print(driver.which_browser)
# GUI.start_download(driver, artist, user, password)
# userinfo = open('userinfo.txt', 'a')
gui = GUI.GUI()

print('fin')

# todo change structure so files are hidden away more neatly
# todo looks like it isn't logging in correctly?
# todo captcha
# todo track down firefox bug- happens before login it seems - fixed?
# todo: check if there's a Tabs folder, and create one if not
# todo: figure out how to make project files folder hidden
# todo:autofill error if there's no data
# low priority:
# todo allow for editing and viewing of a to download text file
# todo change or allow customization to folders
# todo total downloads/downloads finished appearing at end of page
# todo allow for redownload of failures
# todo progress bar
# todo lock window size - headless working so may not be necessary
# todo rewrite scroll_to_bottom without waits, as possible optimization
