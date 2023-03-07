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

# todo problems when downloading a single file
# todo captcha
# todo track down firefox bug- not completing downloads now

# low priority:
# todo allow for editing and viewing of a 'to download' text file
# it would be nice to add and delete, and paste to download field directly from this
# need to read from file to populate table
# button for copying from table line to artist download field
# delete table entry button
# text box and add button
# create events
# todo change or allow customization to folders
# todo total downloads/downloads finished appearing at end of page
# todo allow for redownload of failures
# todo progress bar, example in psgdemos all elements demo
# todo lock window size - headless working so may not be necessary
# todo rewrite scroll_to_bottom without waits, as possible optimization