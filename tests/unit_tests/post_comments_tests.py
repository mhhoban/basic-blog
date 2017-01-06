from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, LoginPage, BlogComposePage, BlogEditPage
from register import registration
from hasher import encode_cookie
from blog_post_tools import (blog_data_parser, store_post, get_all_posts, get_post_comment_total,
                             add_comment, get_post_comments)
import json

from google.appengine.ext import ndb, testbed


class BlogPostTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
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

    def testNewBlogPostHasEmptyComments(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        test_comments = json.loads(test_post.comments)

        self.assertEqual(test_comments, [])

    def testNewBlogComment(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        add_comment(1, 'blarg', 'blarg no like')

        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        test_comments = json.loads(test_post.comments)

        self.assertEqual(test_comments[0]['content'], 'blarg no like')
        self.assertEqual(test_comments[0]['commenter'], 'blarg')

    def testRetrieveBlogComment(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        add_comment(1, 'blarg', 'blarg no like')

        comments = get_post_comments(1)

        self.assertEqual(comments[0]['content'], 'blarg no like')

    def testRetrieveBlogCommentTotal(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        add_comment(1, 'blarg', 'blarg no like')

        comment_total = get_post_comment_total(1)

        self.assertEqual(comment_total, 1)







