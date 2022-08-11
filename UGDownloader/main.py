import DLoader
import GUI
# todo test headless. does window need to be a certain size? restrict resize?
# testing
artist = 'Wormrot'
# account 1
# user = 'mygoodusername'
# password = 'passyword'
# account 2
user = 'jake.c.abbey'
password = '!bRD3*@erWRZ54'
driver = GUI.start_browser(artist)
GUI.start_download(driver, artist, user, password)

# gui = GUI.GUI()

print('fin')
