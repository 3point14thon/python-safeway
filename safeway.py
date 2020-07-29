import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


class SafeWay:

    def __init__(self):
        self.driver = selenium.webdriver.Firefox()
        self.driver.get('https://safeway.com')
        self.sign_in()

    def sign_in(self):
        with open('user_data.txt', 'r') as f:
            user = f.readline()
            password = f.readline()
        try:
            menu = WebDriverWait(self.driver, 45).until(
                EC.presence_of_element_located(
                  (By.LINK_TEXT, 'Sign In / Up')))
        except TimeoutException:
            print("Timedout")
        menu.click()
        self.driver.find_element_by_id('sign-in-modal-link').click()
        self.driver.find_element_by_id('label-email').send_keys(user)
        element = self.driver.find_element_by_id('label-password')
        element.send_keys(password)
        element.send_keys(Keys.ENTER)
