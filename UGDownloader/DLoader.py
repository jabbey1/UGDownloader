import time
from selenium.webdriver.common.by import By


class DLoader:
    def __init__(self, artist, driver):
        self.artist = artist
        self.driver = driver


def gettabs(driver):
    tab_list = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
    tab_list[:] = [x for x in tab_list if x.text.__contains__('Guitar Pro')]
    how_many_tabs = len(tab_list)
    print('Found ' + str(len(tab_list)) + ' Guitar Pro Files')

    # download for each element, skipping pro or official
    for i in range(how_many_tabs):
        tab_list = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
        # TODO find out how slices work
        tab_list[:] = [x for x in tab_list if x.text.__contains__('Guitar Pro')]
        print(tab_list[i].find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))  # print link
        tab_list[i].find_element(By.CSS_SELECTOR, '.HT3w5').click()
        button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
        time.sleep(.1)
        driver.execute_script("window.stop();")  # stop their player from loading
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
        time.sleep(.1)
        driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
        time.sleep(.1)
        # click download button, go back
        # todo comment below line out for testing
        # button.click()  # TODO: why is there a huge delay after this?
        driver.back()

    # todo go to next page and repeat
