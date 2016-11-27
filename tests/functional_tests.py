from selenium import webdriver
from hamcrest import assert_that, contains_string

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import unittest

# caps['marionette'] = True


class NewUserSignUpTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_page_loads(self):

        self.browser.get('http://localhost:8080')

    def test_user_not_signed_in(self):

        self.browser.get('http://localhost:8080')

        try:

            email_field = self.browser.find_element_by_id('email-inputz')

        except NoSuchElementException:

            email_field = False

        self.assertTrue(email_field, 'email_field not detected for non-logged in user')

if __name__ == '__main__':
    unittest.main()
