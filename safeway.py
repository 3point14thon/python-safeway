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
        title_els = self.driver.find_elements_by_class_name('product-title')
        products = [self.mk_product_dict(prdct) for prdct in title_els]
        # optimize product selection here
        product = products[0]
        qty = self.determine_qty(product, amount, unit)
        self.get_qty(product, qty)

    def find_item(self, item):
        search = self.driver.find_element_by_id('skip-main-content')
        search.clear()
        search.send_keys(item)
        search.send_keys(Keys.ENTER)
        sleep(5)

    def determine_qty(self, product, purchase_amount, purchase_unit):
        purchase_unit = homogenize_unit(purchase_unit)
        vol_units = volumeunits.VolumeUnit(0, '_', '_').units
        mass_units = massunits.MassUnit(0, '_', '_').units
        item_unit = product['amount'][1]
        item_amount = product['amount'][0]
        if purchase_unit in mass_units:
            item_amount = massunits.MassUnit(item_amount, item_unit, purchase_unit)
        elif purchase_unit in vol_units:
            if item_unit in vol_units:
                item_amount = volumeunits.VolumeUnit(item_amount, item_unit, purchase_unit)
            else:
                g = massunits.MassUnit(item_amount, item_unit, 'g').doconvert()
                item_amount = volumeunits.VolumeUnit(g, 'ml', purchase_unit)
        else:
            return purchase_amount
        return ceil(purchase_amount / item_amount.doconvert())

    def mk_product_dict(self, title_el):
        product_id = title_el.get_attribute('id')
        rate = self.driver.find_element_by_id(product_id + 'unitPer').text
        price = self.driver.find_element_by_id(product_id + 'price').text
        product = {
                'id': product_id,
                'price': self.parse_price(price),
                'rate': self.parse_rate(rate),
                'title': title_el.text
                }
        product['amount'] = product['price'] / product['rate'][0], product['rate'][1]
        return product

    def parse_rate(self, rate):
        rate = re.split('.\D*(\d*\.?\d*) \/ (\w*).*', rate)[1:-1]
        return float(rate[0]), homogenize_unit(rate[1])

    def parse_price(self, price):
        price = re.split('.\D*(\d*\.?\d*).*', price)
        return float(price[1])

    def get_qty(self, product, qty):
        short_id = product['id'][2:]
        self.element_getter(By.ID, 'addButton_' + short_id, 15).click()
        self.element_getter(By.ID, 'qtyInfo_' + short_id, 10).click()
        product = self.driver.find_element_by_id('qtyInfoControl_' + short_id)
        product.send_keys(str(qty))
        btn_name = 'specify-quantity-more.update-button'
        update = self.driver.find_element_by_class_name(btn_name)
        update.click()
        update.click()
