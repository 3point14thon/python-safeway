import re
from math import ceil
from time import sleep
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from unitconvert import massunits, volumeunits
from unit_homogenizer import homogenize_unit


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
        product = products[0]
        qty = self.determine_qty(product.text, amount, unit)
        product_id = product.get_attribute('id')
        self.driver.find_element_by_css_selector('#' + product_id + '-qty > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)').click()
        self.element_getter(By.ID, 'qtyInfo_' + product_id[2:], 10).click()
        product = self.driver.find_element_by_id('qtyInfoControl_' + product_id[2:])
        product.send_keys(str(qty))
        update = self.driver.find_element_by_class_name('specify-quantity-more.update-button')
        update.click()
        update.click()

    def find_item(self, item):
        search = self.driver.find_element_by_id('skip-main-content')
        search.clear()
        search.send_keys(item)
        search.send_keys(Keys.ENTER)
        sleep(5)

    def parse_item_txt(self, product_text):
        pattern = '.+- (\d*\.?\d*)-?(\d*\.?\d*)?([^\(]*)'
        item_info = re.split(pattern, product_text)[1:-1]
        if not len(item_info):
            return 1, product_text
        elif item_info[1]:
            qty, amount, unit = item_info
            return int(qty) * float(amount), unit
        else:
            amount, _, unit = item_info
            return float(amount), unit

    def determine_qty(self, product_txt, purchase_amount, purchase_unit):
        purchase_unit = homogenize_unit(purchase_unit)
        item_amount, item_unit = self.parse_item_txt(product_txt)
        item_unit = homogenize_unit(item_unit)
        if purchase_unit in volumeunits.VolumeUnit(0, '_', '_').units:
            item_amount = volumeunits.VolumeUnit(item_amount, item_unit, purchase_unit)
        elif purchase_unit in massunits.MassUnit(0, '_', '_').units:
            item_amount = massunits.MassUnit(item_amount, item_unit, purchase_unit)
        else:
            return item_amount
        return ceil(purchase_amount / item_amount.doconvert())
