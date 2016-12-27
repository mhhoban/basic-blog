from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest
import json
from main import MainPage, Register, LoginPage, BlogComposePage, BlogEditPage, LikePost
from register import registration
from hasher import encode_cookie
from blog_post_tools import (blog_data_parser, store_post, get_all_posts, get_post_author, get_post_data,
                             update_post, add_post_like)
from db_schema import Post

from google.appengine.ext import ndb, testbed


class PostLikeTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
                                       ('/like.html', LikePost),
                                       ('/blog-edit.html', BlogEditPage),
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

    def subjectPostGeneratorA(self):

        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

    def generateLoggedInUserA(self):
        registration('test@user', 'secret', 'testuserz')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

    def generateLoggedInUserB(self):
        registration('test@user', 'secret', 'testuser')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

    def testLikeLoggedInResponse(self):

        registration('test@user', 'secret', 'testuser')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

        response = self.testapp.get('/like.html?title_id=1')

        self.assertEqual(response.status_int, 200)

    def testLikeNotLoggedInResponse(self):

        response = self.testapp.get('/like.html?title_id=blarg')

        self.assertEqual(response.status_int, 302)

    def testDefaultLikeCount(self):

        self.subjectPostGeneratorA()
        sample_post = get_post_data(1)

        likes = json.loads(sample_post.likes)
        self.assertEqual(len(likes), 0)

    def testVerifyPostExistsTrue(self):

        self.generateLoggedInUserA()
        self.subjectPostGeneratorA()

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'cannot like own post')

    def testVerifyPostExistsFalse(self):

        self.generateLoggedInUserA()

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'no such post')

    def testVerifyCannotLikeOwnPost(self):
        self.generateLoggedInUserA()
        self.subjectPostGeneratorA()

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'cannot like own post')

    def testVerifyCanDifferentiateUserFromAuthor(self):
        self.generateLoggedInUserB()
        self.subjectPostGeneratorA()

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'new like added!')

    def testRecognizeNewLiker(self):
        self.generateLoggedInUserB()
        self.subjectPostGeneratorA()

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'new like added!')

    def testRejectExistingLiker(self):
        self.generateLoggedInUserB()
        self.subjectPostGeneratorA()
        add_post_like(1, 'testuser')

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'already liked')

    def testAddNewLike(self):
        self.generateLoggedInUserB()
        self.subjectPostGeneratorA()
        add_post_like(1, 'testuseri')
        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'new like added!')