from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest
import re

from main import Cookie_baker, MainPage


class Web_Tests(unittest.TestCase):

    def setUp(self):
        """Sets up to mock app for unit tests"""
        # create mock web app for testing
        app = webapp2.WSGIApplication([('/', MainPage),
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

    def testMainPageLoggedInResponse(self):
        """
        tests that main page recognizes a user that is logged in
        :return:
        """
        self.testapp.set_cookie('user-id', 'John Doe')
        response = self.testapp.get('/')
        assert_that(response.body, contains_string('John Doe'))


if __name__ == '__main__':
    unittest.main()


# from hamcrest import *
# import unittest
#
# class BiscuitTest(unittest.TestCase):
#     def testEquals(self):
#
#         a = 'bllllllarg'
#         b = 'bllll'
#
#         assert_that(a, contains_string(b))
#
# if __name__ == '__main__':
#     unittest.main()