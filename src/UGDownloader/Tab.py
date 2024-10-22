import json
from datetime import datetime
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Utils import config

INFO_TABLE_SELECTOR = config.get('Selectors', 'INFO_TABLE_SELECTOR')
AUTHOR_SELECTOR = config.get('Selectors', 'AUTHOR_SELECTOR')
LAST_EDIT_SELECTOR = config.get('Selectors', 'LAST_EDIT_SELECTOR')

class Tab(object):
    """An Object for each tab. Can be of any type, and if text, can contain whole text."""
    def __init__(self, url: str):
        self.url = url
        self.tab_id = self.url.rsplit('-', 1)[1]
        self.artist = ''
        self.song_name = ''
        self.format = ''
        self.filesize = ''
        self.tuning = ''
        self.capo = ''
        self.difficulty = ''
        self.key = ''
        self.instruments = ''
        self.version = '1'
        self.author = ''
        self.last_edit = None
        self.date_downloaded = None
        self.rating_value = None
        self.rating_count = 0
        self.text = ''

    def read_info(self, driver: webdriver):
        """Use various html elements to find necessary info about the tab."""
        if driver.current_url != self.url:
            driver.get(self.url)

        data = driver.find_element(By.NAME, 'keywords')
        keywords_text = str(data.get_attribute("content"))
        self.artist, remaining = keywords_text.split(' - ', 1)
        self.song_name, remaining = remaining.split(' (', 1)
        self.format, remaining = remaining.split('), ', 1)
        # Unfortunately some it appears that artists with stylized names have the stylized text in this next slot.
        # e.g. 'ISIS', when the text where artist is Isis. I'll leave it in parenthesis.
        # Sometimes a tab will have an extra title label, like 'live' or 'acoustic',
        # but it will be separate from the title in the keywords list
        remaining = remaining.split(', ')
        if remaining[1] != self.artist:
            self.song_name += (' (' + remaining[1] + ')')

        # table above the tab player has lots of extra info
        # info_table = driver.find_element(By.CSS_SELECTOR, INFO_TABLE_SELECTOR)
        info_table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, INFO_TABLE_SELECTOR)))

        rows = info_table.find_elements(By.TAG_NAME, "tr")
        table_data = {}
        for row in rows:
            headers = row.find_elements(By.TAG_NAME, "th")
            table_text = row.find_elements(By.TAG_NAME, "td")
            for he, te in zip(headers, table_text):
                table_data[he.text] = te.text
        # not all information will always be present
        # self.format = table_data.get('File format:', self.format)
        self.filesize = table_data.get('Filesize:', self.filesize)
        self.capo = table_data.get('Capo:', self.capo)
        self.tuning = table_data.get('Tuning:', self.tuning)
        self.difficulty = table_data.get('Difficulty:', self.difficulty)
        self.key = table_data.get('Key:', self.key)
        # they haven't noticed the typo in 'instuments'??
        self.instruments = table_data.get('Instuments:', self.instruments)

        # version is not included if there's only 1, which is the default value
        if '(ver ' in driver.title:
            self.version = driver.title.split('(ver ')[1].split(')')[0]

        author = driver.find_element(By.CSS_SELECTOR, AUTHOR_SELECTOR).text
        self.author = author.split(' ')[0]

        edit_text = driver.find_element(By.CSS_SELECTOR, LAST_EDIT_SELECTOR).text
        parts = edit_text.split()
        last_edit = ' '.join(parts[-3:])
        self.last_edit = datetime.strptime(last_edit, '%b %d, %Y')
        try:
            script_tag = driver.find_element(By.XPATH, '//script[contains(text(), "ratingValue")]')
            script_content = script_tag.get_attribute('innerHTML')
            data = json.loads(script_content)
            self.rating_value, self.rating_count = data['aggregateRating']['ratingValue'], data['aggregateRating'][
                'ratingCount']
        except selenium.common.exceptions.NoSuchElementException:
            self.rating_value, self.rating_count = None, 0


    def print_attributes(self):
        print(f"{self.url=}")
        print(f"{self.artist=}")
        print(f"{self.song_name=}")
        print(f"{self.format=}")
        print(f"{self.filesize=}")
        print(f"{self.tuning=}")
        print(f"{self.capo=}")
        print(f"{self.difficulty=}")
        print(f"{self.key=}")
        print(f"{self.tab_id=}")
        print(f"{self.instruments=}")
        print(f"{self.version=}")
        print(f"{self.rating_value=}")
        print(f"{self.rating_count=}")
        print(f"{self.author=}")
        print(f"{self.last_edit=}")


def start_test_driver() -> webdriver:
    chrome_service = ChromeService()
    new_driver = webdriver.Chrome(service=chrome_service)
    return new_driver


if __name__ == "__main__":
    pass
