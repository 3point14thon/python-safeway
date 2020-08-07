import re
from time import sleep
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
        #TODO make sure entire page loads before searching for elements
        sleep(5) # waits for page to load
        self.element_getter(By.LINK_TEXT, 'Sign In / Up', 45).click()
        self.element_getter(By.ID, 'sign-in-modal-link', 5).click()
        self.driver.find_element_by_id('label-email').send_keys(user)
        element = self.driver.find_element_by_id('label-password')
        element.send_keys(password)
        element.send_keys(Keys.ENTER)

    def element_getter(self, by, value, delay):
        try:
            element = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            print("Timedout")

    def add_item(self, item, amount, unit):
        self.find_item(item)
        products = self.driver.find_elements_by_class_name('product-title')
        #optimize product selection here
        qty = self.determine_qty(products.text)
        product_id = products[0].get_attribute('id')
        self.driver.find_element_by_css_selector('#' + product_id + '-qty > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()

    def find_item(self, item):
        search = self.driver.find_element_by_id('skip-main-content')
        search.clear()
        search.send_keys(item)
        search.send_keys(Keys.ENTER)
        sleep(5)

    def determine_qty(self, product_txt):
        pattern = '.+- (\d+)-?(\d+)?([^\(]*)'
        item_info = re.split(pattern, products.text)[1:-1]
        if not len(item_info):
            #assume produce, use density of water to approximate qty or use qty directly
        elif item_info[1]:
            qty, amount, unit = item_info
        else:
            amount, _, unit = item_info

