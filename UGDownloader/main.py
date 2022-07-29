from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()  # create instance of browser

# driver.get("http://www.python.org")  # Navigate to a webpage
# assert "Python" in driver.title  # The next line is an assertion to confirm that title has “Python” word in it:???
# elem = driver.find_element(By.NAME, "q")  # finding element by its name attribute
# elem.clear()  # clear prepopulated text
# elem.send_keys("pycon")  # send keys to element
# elem.send_keys(Keys.RETURN)  # hit return with keys
# assert "No results found." not in driver.page_source
# driver.close()

# driver.get("https://www.ultimate-guitar.com/")  # Manually go to homepage and search
# searchElem = driver.find_element(By.NAME, "value")
# searchElem.clear()
# searchElem.send_keys("radiohead")
# searchElem.send_keys(Keys.RETURN)


# get artist text input here
artist = 'Radiohead'  # case-sensitive match
driver.get('https://www.ultimate-guitar.com/search.php?search_type=bands&value=' + artist)
driver.find_element(By.LINK_TEXT, artist).click()
driver.find_element(By.LINK_TEXT, 'Guitar Pro').click()
