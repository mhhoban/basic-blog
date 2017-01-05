from selenium import webdriver
from hamcrest import assert_that, contains_string
from time import sleep

from selenium.webdriver.common.keys import Keys
from auto_tools import AppServer, AutoTestTools

from selenium.common.exceptions import NoSuchElementException

import unittest



class LogInTests(unittest.TestCase):

    def setUp(self):

        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument("--incognito")

        self.browser = webdriver.Chrome(chrome_options=chrome_opts)
        self.browser.set_window_size(1300, 1300)
        self.test_server = AppServer()
        self.test_server.start_server()

        self.tools = AutoTestTools()

        sleep(3)

    def tearDown(self):
        self.browser.quit()
        self.test_server.stop_app_server()

    def test_user_log_in(self):

        self.tools.register_user_alpha()

        # User visits the blog, which loads successfully
        self.browser.get('http://localhost:8080')

        sleep(2)

        # Then sees a field for an email input
        try:
            email_field = self.browser.find_element_by_id('user_id')

        except NoSuchElementException:
            email_field = False

        self.assertTrue(email_field, 'email_field not detected for non-logged in user')

        # Then sees a field for a password input
        try:
            password_field = self.browser.find_element_by_id('password')

        except NoSuchElementException:
            password_field = False

        self.assertTrue(password_field, 'password_field not detected for non-logged in user')

        # Then sees a login button
        try:
            login_button = self.browser.find_element_by_name('login-submit')

        except NoSuchElementException:
            login_button = False

        self.assertTrue(login_button, 'login button not detected for non-logged in user')

        # ------------------------ Try Logging in as user

        email_field.send_keys('a@a.a')
        password_field.send_keys('thing')

        login_button.click()

        # ------------------------- Confirm logged in as user

        try:
            penname = self.browser.find_element_by_xpath("//*/div[@class='user-greeting']/h3")
        except NoSuchElementException:
            penname = False

        self.assertTrue(penname, 'User name not showing after Login')
        assert_that(penname.text, contains_string('thing'))

if __name__ == '__main__':
    unittest.main()
