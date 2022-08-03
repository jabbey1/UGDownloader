import time
from selenium.webdriver.common.by import By
from line_profiler_pycharm import profile


class DLoader:
    pass


@profile
def get_tabs(driver):
    tab_list = driver.find_elements(By.CLASS_NAME, 'LQUZJ')
    tab_links = []
    tab_list[:] = [x for x in tab_list if x.text.__contains__('Guitar Pro')]
    for i in tab_list:
        tab_links.append(i.find_element(By.CSS_SELECTOR, '.HT3w5').get_attribute('href'))
    how_many_tabs = len(tab_list)
    print('Found ' + str(how_many_tabs) + ' Guitar Pro Files')
    # download for each element, skipping pro or official
    for i in range(how_many_tabs):
        print(tab_links[i])
        driver.get(str(tab_links[i]))
        button = driver.find_element(By.CSS_SELECTOR, 'button.exTWY:nth-child(2)')
        scroll_to_bottom(driver)
        # todo comment below line out for testing
        # todo why does button click take so long?
        # button.click()


def scroll_to_bottom(driver):
    # todo check if times can be cut/shortened
    time.sleep(.1)
    driver.execute_script("window.stop();")  # stop their player from loading
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # scroll to bottom of page to see button
    time.sleep(.1)
    driver.execute_script(
        "window.scrollTo(0,document.body.scrollHeight)")  # would be nice to get rid of browser bounce
    time.sleep(.1)
