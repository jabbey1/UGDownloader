import time
from selenium.webdriver.common.by import By
from line_profiler_pycharm import profile

class DLoader:
    pass

@profile
def get_tabs(driver):
    tab_list = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
    print('Found ' + str(len(tab_list)) + ' Guitar Pro Files')
    tab_list[:] = [x for x in tab_list if x.text.__contains__('Guitar Pro')]
    how_many_tabs = len(tab_list)
    print('Found ' + str(len(tab_list)) + ' Guitar Pro Files')

    # download for each element, skipping pro or official
    for i in range(how_many_tabs):
        tab_list = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
        # TODO would be really nice to speed up below line, iterating through takes forever
        # TODO but it doesn't seem like the list stays valid after clicking back
        # TODO maybe if redesigned to open in new tabs, tablist could stay intact
        tab_list[:] = [x for x in tab_list if x.text.__contains__('Guitar Pro')]
        print(tab_list[i].find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))  # print link
        # tab_list[i].find_element(By.CSS_SELECTOR, '.HT3w5').click()
        # button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
        # time.sleep(.1)
        # driver.execute_script("window.stop();")  # stop their player from loading
        # driver.execute_script(
        #     "window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
        # time.sleep(.1)
        # driver.execute_script(
        #     "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
        # time.sleep(.1)
        # # click download button, go back
        # # todo comment below line out for testing
        # # button.click()
        # driver.back()

    # todo go to next page and repeat
