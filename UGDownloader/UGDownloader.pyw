import logging
import CTKGUI

logging.basicConfig(filename='myapp.log', level=logging.DEBUG, format='%(levelname)s:%(message)s')
logging.info('Started')

app = CTKGUI.App()
app.mainloop()

logging.info('Finished')