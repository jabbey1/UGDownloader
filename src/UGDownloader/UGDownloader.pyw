import datetime
import logging
import CTKGUI
from Utils import folder_check

folder_check()
logging.basicConfig(filename='_UGDownloaderFiles/myapp.log', level=logging.INFO, format='%(levelname)s:%(message)s')
logging.info('Started @ ' + str(datetime.datetime.now()))

app = CTKGUI.App()
app.mainloop()

logging.info('Finished @ ' + str(datetime.datetime.now()))
