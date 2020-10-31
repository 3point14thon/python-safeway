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
import safeway
from safeway.__init__ import homogenize_unit


class SafeWay:
    '''
    An instance of this class will create a browser
    session at safeway.com and log in.

    __init__ method creates driver attribute starts browsing session and logs
    into safeway.com using login info from user_data.txt

    Attributes:
        driver(driver): the selenium driver object contorolling the browsing
        session
    '''

    def __init__(self):
        self.driver = selenium.webdriver.Firefox()
        self.driver.get('https://safeway.com')
        self.sign_in()

    def sign_in(self):
        '''
        Signs into safeway.com using user_data.txt
        '''
        user, password = self.get_user_data()
        # TODO make sure entire page loads before searching for elements
        sleep(5)  # waits for page to load
        self.element_getter(By.LINK_TEXT, 'Sign In / Up', 45).click()
        self.element_getter(By.ID, 'sign-in-modal-link', 5).click()
        self.driver.find_element_by_id('label-email').send_keys(user)
        element = self.driver.find_element_by_id('label-password')
        element.send_keys(password)
        element.send_keys(Keys.ENTER)

    def get_user_data(self):
        '''
        returns username and password. prompts user for data and
        writes to file if not found.

        Returns:
            username and password as a tuple of strings. (user, pass)
        '''
        file_dir = safeway.__file__.replace('__init__.py', 'user_data.txt')
        with open(file_dir, 'r+') as f:
            user = f.readline()
            if user == '':
                print('User profile not found')
                print('Please provide login info')
                user = input('User name: ')
                f.write(user + '\n')
                password = input('Password: ')
                f.write(password)
            else:
                password = f.readline()
            return (user, password)

    def element_getter(self, by, value, delay):
        '''
        waits for delay seconds or until element type by with value is loaded.

        Args:
            by(type): type of web element
            value(str): value used to identify web element
            delay(int): time in seconds to wait for element to load

        Returns:
            web element described by by and value
        '''
        try:
            element = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException:
            print("Timedout")

    def add_item(self, item, amount, unit):
        '''
        adds enough item to cart to satisfy amount of unit.

        Args:
            item(str): item to be added to cart
            amount(float): minimum amount of item to be added
            unit(str): unit amount is measured in
        '''
        self.find_item(item)
        title_els = self.driver.find_elements_by_class_name('product-title')
        products = [self.mk_product_dict(prdct) for prdct in title_els]
        # optimize product selection here
        product = products[0]
        qty = self.determine_qty(product, amount, unit)
        self.get_qty(product, qty)

    def find_item(self, item):
        '''
        searches for item on safeway website

        Args:
            item(str): item to be searched for
        '''
        search = self.driver.find_element_by_id('skip-main-content')
        search.clear()
        search.send_keys(item)
        search.send_keys(Keys.ENTER)
        sleep(5)

    def determine_qty(self, product, purchase_amount, purchase_unit):
        '''
        determines the minimum quantity of product needed to fulfill
        purchase_amount in purchase_unit

        Note:
            when product["unit"] is in mass and purchase_unit is in volume
            product density is assumed to be that of water

        Args:
            product(dict): dict containing aspects of product to be added
            purchase_amount(float): amount of product needed
            purchase_unit(str): unit purchase_amount is measured in

        Returns:
            minimum quantity of product needed to fulfill purchase_amount
            in purchase_unit as an int
        '''
        purchase_unit = homogenize_unit(purchase_unit)
        vol_units = volumeunits.VolumeUnit(0, '_', '_').units
        mass_units = massunits.MassUnit(0, '_', '_').units
        item_unit = product['amount'][1]
        item_amount = product['amount'][0]
        if purchase_unit in mass_units:
            item_amount = massunits.MassUnit(item_amount,
                                             item_unit,
                                             purchase_unit)
        elif purchase_unit in vol_units:
            if item_unit in vol_units:
                item_amount = volumeunits.VolumeUnit(item_amount,
                                                     item_unit,
                                                     purchase_unit)
            else:
                g = massunits.MassUnit(item_amount, item_unit, 'g').doconvert()
                item_amount = volumeunits.VolumeUnit(g, 'ml', purchase_unit)
        else:
            return purchase_amount
        return ceil(purchase_amount / item_amount.doconvert())

    def mk_product_dict(self, title_el):
        '''
        creates dictionary containing product attributes

        Args:
            title_el(FirefoxWebElement): title element of product dict
                will be made for
        '''
        product_id = title_el.get_attribute('id')
        rate = self.driver.find_element_by_id(product_id + 'unitPer').text
        price = self.driver.find_element_by_id(product_id + 'price').text
        product = {
                'id': product_id,
                'price': self.parse_price(price),
                'rate': self.parse_rate(rate),
                'title': title_el.text
                }
        product['amount'] = (product['price'] / product['rate'][0],
                             product['rate'][1])
        return product

    def parse_rate(self, rate):
        '''
        returns parsed product rate as tuple, (float, str),
        representing $ per unit
        '''
        rate = re.split('.\D*(\d*\.?\d*) \/ (\w*).*', rate)[1:-1]
        return float(rate[0]), homogenize_unit(rate[1])

    def parse_price(self, price):
        '''
        parces product price, returns total price as float
        '''
        price = re.split('.\D*(\d*\.?\d*).*', price)
        return float(price[1])

    def get_qty(self, product, qty):
        '''
        adds qty of product to cart

        Args:
            product(dict): dict containing aspects of product to be added
            qty(int): amount of item to be added
        '''
        short_id = product['id'][2:]
        self.element_getter(By.XPATH, '//quantity-stepper[@id="' + product['id'] + '-qty"]//div[@id="addButton"]', 15).click()
        sleep(10)
        self.element_getter(By.ID, 'qtyInfo_' + short_id, 10).click()
        product = self.driver.find_element_by_id('qtyInfoControl_' + short_id)
        product.send_keys(str(qty))
        btn_name = 'specify-quantity-more.update-button'
        update = self.driver.find_element_by_class_name(btn_name)
        update.click()
        update.click()
