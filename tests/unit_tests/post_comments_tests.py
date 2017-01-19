from blog_post_tools import (add_comment, edit_comment, gen_comment_id, get_post_comment_total,
                             get_post_comments, get_timestamp, store_post,)
from google.appengine.ext import ndb, testbed
from hamcrest import assert_that, contains_string, is_not
from hasher import encode_cookie
from main import BlogComposePage, BlogEditPage, LoginPage, MainPage, Register
from register import registration

import json
import unittest
import webapp2
import webtest


class BlogPostTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
                                       ('/blog-edit.html', BlogEditPage),
                                       ])

        self.testapp = webtest.TestApp(app)
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()

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

    def testCommentIdGeneration(self):

        timestamp = get_timestamp()

        id = gen_comment_id('a', 'aa', 'title', timestamp)

        if id:
            id_gen = True

        else:
            id_gen = False

        assert_that(id_gen, is_not(False))

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

    def testCommentEdit(self):

        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        add_comment(1, 'blarg', 'blarg no like')

        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        test_comments = json.loads(test_post.comments)

        self.assertEqual(test_comments[0]['content'], 'blarg no like')
        self.assertEqual(test_comments[0]['commenter'], 'blarg')

        edit_comment(1, test_comments[0]['comment_id'], 'blarg edited!')

        test_post = test_post_key.get()
        test_comments = json.loads(test_post.comments)

        self.assertEqual(test_comments[0]['content'], 'blarg edited!')
