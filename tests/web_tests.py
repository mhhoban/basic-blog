from hamcrest import assert_that, contains_string
from db_schema import Users

import unittest
import webapp2
import webtest

from main import Cookie_baker, MainPage, Register, RegisterParse
from regform_checks import valid_email_check, passwords_match_check


class Web_Tests(unittest.TestCase):

    def setUp(self):
        """Sets up to mock app for unit tests"""
        # create mock web app for testing
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/registration-parse.html', RegisterParse),
                                       ('/cookie', Cookie_baker)])
        # wrap the test app:
        self.testapp = webtest.TestApp(app)

    def testCookieHashing(self):
        """
        tests that visiting the main page detects cookies appropriately
        :return:
        """

        self.testapp.set_cookie('user-id', 'test-hash,420ad9ff2d6c88f4782ebbd7a4f03a82')

        response = self.testapp.get('/')
        assert_that(response.body, contains_string('test-hash'))

    # def testRegistrationCompleteForm(self):
    #
    #     # test that registration-parse detects completed form
    #     response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing', 'password': 'thing',
    #                                                               'password_rep': 'thing'})
    #
    #     assert_that(response.body, contains_string('registration complete!'))



if __name__ == '__main__':
    unittest.main()
