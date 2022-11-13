import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


# captcha css selectors
# #captchak8gPWM_TLJs0GssOrg0gG > div:nth-child(1) > div:nth-child(1) > iframe:nth-child(1)
# title="reCAPTCHA"
# todo convert this java code
def handle_captcha(driver):
    WebDriverWait(driver, 10).until(ec.frameToBeAvailableAndSwitchToIt(
        By.xpath("//iframe[starts-with(@name, 'a-') and starts-with(@src, 'https://www.google.com/recaptcha')]")));

    WebDriverWait(driver, 20).until(
        ec.elementToBeClickable(By.cssSelector("div.recaptcha-checkbox-checkmark"))).click();

    for _ in range(100):  # or loop forever, but this will allow it to timeout if the user falls asleep or whatever
        if driver.get_current_url.find("captcha") == -1:
            break
        time.sleep(6)  # wait 6 seconds which means the user has 10 minutes before timeout occurs

    # todo another possible method:
    WebDriverWait(driver, 10).until(ec.frame_to_be_available_and_switch_to_it(
        (By.CSS_SELECTOR, "iframe[src^='https://www.google.com/recaptcha/api2/anchor?']")))
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR,
                                                                "span.recaptcha-checkbox.goog-inline-block.recaptcha-checkbox-unchecked.rc-anchor-checkbox"))).click()
    driver.switch_to_default_content()
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-primary.block.full-width.m-b"))).click()
    time.sleep(.5)

