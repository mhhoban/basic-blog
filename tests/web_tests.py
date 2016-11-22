from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import Cookie_baker, MainPage, Register


class Web_Tests(unittest.TestCase):

    def setUp(self):
        """Sets up to mock app for unit tests"""
        # create mock web app for testing
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/cookie', Cookie_baker)])
        # wrap the test app:
        self.testapp = webtest.TestApp(app)

    def testMainPageLoads(self):
        """tests that main page loads successfully"""
        response = self.testapp.get('/')
        self.assertEqual(response.status_int, 200)

    def testMainPageNotLoggedInResponse(self):
        """
        tests that main page shows login fields when a visitor is not
        logged in as a user

        """
        response = self.testapp.get('/')
        assert_that(response.body, contains_string('login-form'))

    def testCookieHashing(self):
        """
        tests that visiting the main page detects cookies appropriately
        :return:
        """

        self.testapp.set_cookie('user-id', 'test-hash,420ad9ff2d6c88f4782ebbd7a4f03a82')

        response = self.testapp.get('/')
        assert_that(response.body, contains_string('test-hash'))

    def testRegistrationPage(self):
        """
        tests behavior of registration page
        :return:
        """
        response = self.testapp.get('/register.html')
        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('Register For Basic Blog!'))


if __name__ == '__main__':
    unittest.main()
