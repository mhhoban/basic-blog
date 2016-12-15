from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, LoginPage, BlogComposePage
from register import registration
from cookie_hasher import encode_cookie, verify_cookie

from google.appengine.ext import testbed


class LoginTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
                                       ])
        # wrap the test app:
        self.testapp = webtest.TestApp(app)

        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        # ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

    def testMainPageNotLoggedInResponse(self):
        """
        tests that main page shows login fields when a visitor is not
        logged in as a user

        """
        response = self.testapp.get('/')
        assert_that(response.body, contains_string('login-form'))

    def testUserCookieHashing(self):
        """
        Verify user cookie encodes and decodes correctly
        :return:
        """

        hashed_cookie = encode_cookie('thing@thing')

        # TODO integrate cookie split into function itself to avoid this code all over
        hashed_cookie = hashed_cookie.split('-')
        correct_hash = verify_cookie(hashed_cookie)

        self.assertEqual(correct_hash, True, 'False Negative on hash decoding')

        hashed_cookie = encode_cookie('thingz@thing')

        # TODO integrate cookie split into function itself to avoid this code all over
        hashed_cookie = hashed_cookie.split('-')
        hashed_cookie[0] = 'blarg'

        correct_hash = verify_cookie(hashed_cookie)

        self.assertEqual(correct_hash, False, 'False positive on hash decoding')

    def testIncompleteLoginFields(self):

        response = self.testapp.post('/login.html', {'user_id': 'thing@thing.thing'})

        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('incomplete'))

    def testInvalidEmail(self):

        response = self.testapp.post('/login.html', {'user_id': 'thingz@thing.thing', 'password': 'blarg'})

        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('invalid'))

    def testIncorrectPassword(self):

        registration('thing@thing', 'secret', 'thing')

        response = self.testapp.post('/login.html', {'user_id': 'thing@thing', 'password': 'secretz'})

        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('invalid'))

    def testValidLogin(self):

        registration('thingz@thingz', 'secret', 'thingz')

        response = self.testapp.post('/login.html', {'user_id': 'thingz@thingz', 'password': 'secret'})

        self.assertEqual(response.status_int, 302)

        assert_that(response.headers['Location'], contains_string('/'))

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('thingz'))