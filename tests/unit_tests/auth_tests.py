from google.appengine.ext import testbed
from hamcrest import assert_that, contains_string
from hasher import encode_cookie
from main import MainPage, Register, LoginPage, BlogComposePage
from register import registration

import unittest
import webapp2
import webtest


class AuthTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
                                       ])
        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

    def tearDown(self):
        self.testbed.deactivate()

    def testNewAuthIndexNotLoggedIn(self):

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('Register'))

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
