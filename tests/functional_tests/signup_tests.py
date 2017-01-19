from auto_tools import AppServer
from hamcrest import assert_that, contains_string
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from time import sleep

import unittest


class SignupTests(unittest.TestCase):

    def setUp(self):

        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument("--incognito")

        self.browser = webdriver.Chrome(chrome_options=chrome_opts)
        self.browser.set_window_size(1300, 1300)

        self.test_server = AppServer()
        self.test_server.start_server()
        sleep(3)

    def tearDown(self):
        self.browser.quit()
        self.test_server.stop_app_server()

    def test_user_signup(self):

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

        # Then sees a registration link
        try:
            register_link = self.browser.find_element_by_xpath("//*/div[@class='signup-link']/a")

        except NoSuchElementException:
            register_link = False

        self.assertTrue(register_link, 'register link not detected for non-logged in user')

        # Needing to register, the visitor clicks the registration link

        register_link.click()

        sleep(3)
        # Which brings the visitor to the registration page

        registration_headline = self.browser.find_element_by_xpath("//*/div[@class='signup-form']/h3")

        assert_that(registration_headline.text, contains_string('Register For Basic Blog!'))

        # where the user fills in their username

        try:
            email_field = self.browser.find_element_by_id('email-input')

        except NoSuchElementException:
            email_field = False

        self.assertTrue(email_field, 'Email reg field not found')

        email_field.send_keys('a@a.a')
        sleep(1)
        assert_that(email_field.get_attribute('value'), contains_string('a@a.a'))

        # and fills in a pen name

        try:
            penname_field = self.browser.find_element_by_id('penname')

        except NoSuchElementException:
            penname_field = False

        self.assertTrue(penname_field, 'penname field not found')

        penname_field.send_keys('thing')
        sleep(1)
        assert_that(penname_field.get_attribute('value'), contains_string('thing'))

        # and fills in a password

        try:
            password_field = self.browser.find_element_by_id('password-input')

        except NoSuchElementException:
            password_field = False

        self.assertTrue(password_field, 'password field not found')

        password_field.send_keys('thing')
        sleep(1)
        assert_that(password_field.get_attribute('value'), contains_string('thing'))

        # and repeats the password

        try:
            password_field_rep = self.browser.find_element_by_id('password-input-repeat')

        except NoSuchElementException:
            password_field_rep = False

        self.assertTrue(password_field_rep, 'password rep field not found')

        password_field_rep.send_keys('thing')
        sleep(1)
        assert_that(password_field_rep.get_attribute('value'), contains_string('thing'))

        # and clicks the submit button

        try:
            register_submit_button = self.browser.find_element_by_xpath("//*/button")

        except NoSuchElementException:
            register_submit_button = False

        register_submit_button.click()
        sleep(1)

        # successfully completing the sign up process, the user is re-directed to the homepage and is welcomed
        # by their nom de plume

        try:
            penname = self.browser.find_element_by_xpath("//*/div[@class='user-greeting']/h3")
        except NoSuchElementException:
            penname = False

        self.assertTrue(penname, 'User name not showing after registration')
        assert_that(penname.text, contains_string('thing'))
