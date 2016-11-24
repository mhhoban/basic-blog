from hamcrest import assert_that, contains_string

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

    def testRegistrationConnection(self):
        """
        tests that the page that receives and processes signup input is working
        :return:
        """

        # test that route to registration-parse is working
        response = self.testapp.post('/registration-parse.html')
        assert response

    def testRegistrationCompleteForm(self):

        # test that registration-parse detects completed form
        response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing', 'password': 'thing',
                                                                  'password_rep': 'thing'})

        assert_that(response.body, contains_string('registration complete!'))

    def testRegistrationIncompleteForm(self):

        # test that function can handle incomplete form correctly
        response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing@thing.thing' +
                                                                  '&errors=incomplete'))

        response = self.testapp.get('/register.html?email=thing@thing.thing&errors=incomplete')

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('incomplete'))

    def testRegistrationInvalidEmail(self):

        # test that registration-parse detects invalid email
        response = self.testapp.post('/registration-parse.html', {'email': 'thing', 'password': 'thing',
                                                                  'password_rep': 'thing'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing' +
                                                                  '&errors=invalid_email'))

        response = self.testapp.get('/register.html?email=thing&errors=invalid_email')

        assert_that(response.body, contains_string('thing'))
        assert_that(response.body, contains_string('invalid_email'))

    def testRegistrationPasswordMisMatch(self):

        # test that registration-parse detects mismatched passwords in form

        response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing', 'password': 'thing',
                                                                  'password_rep': 'things'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing@thing.thing' +
                                                                  '&errors=mismatched_passwords'))

        response = self.testapp.get('/register.html?email=thing@thing.thing&errors=mismatched_passwords')

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('mismatched_passwords'))

if __name__ == '__main__':
    unittest.main()
