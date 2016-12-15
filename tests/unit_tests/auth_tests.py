from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, LoginPage, BlogComposePage
from register import registration
from cookie_hasher import encode_cookie
from google.appengine.ext import testbed


class DbTests(unittest.TestCase):

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

    def testNewAuthIndexNotLoggedIn(self):

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('Not a Member? Register!'))

    def testNewAuthIndexLoggedIn(self):

        registration('test@user', 'secret', 'testuser')

        hashed_cookie = encode_cookie('test@user')

        self.testapp.set_cookie('user-id', hashed_cookie)
        response = self.testapp.get('/')

        assert_that(response.body, contains_string('testuser'))

    def testNewAuthBlogComposeNotLoggedIn(self):

        response = self.testapp.get('/blog-compose.html')
        self.assertEqual(response.status_int, 302)

    def testNewAuthBlogComposeLoggedIn(self):

        registration('test@user', 'secret', 'testuser')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

        response = self.testapp.get('/blog-compose.html')

        self.assertEqual(response.status_int, 200)

    def testNewAuthBlogComposeParseNotLoggedIn(self):

        response = self.testapp.post('/blog-compose.html', {'title': 'thing_title', 'content': 'thing_content'})

        self.assertEqual(response.status_int, 302)