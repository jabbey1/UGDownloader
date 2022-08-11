import DLoader
import GUI

# testing
artist = 'Radiohead'
user = 'mygoodusername'
password = 'passyword'
driver = GUI.start_browser(artist)
GUI.start_download(driver, artist, user, password)

# gui = GUI.GUI()

print('fin')
