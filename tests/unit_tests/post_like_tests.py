from blog_post_tools import (add_post_like, get_post_data, store_post,)
from google.appengine.ext import ndb, testbed
from hasher import encode_cookie
from main import BlogComposePage, BlogEditPage, LikePost, LoginPage, MainPage, Register
from register import registration

import json
import unittest
import webapp2
import webtest


class PostLikeTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
                                       ('/like.html', LikePost),
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
        self.assertEqual(response.body, 'Success')

    def testRecognizeNewLiker(self):
        self.generateLoggedInUserB()
        self.subjectPostGeneratorA()

        response = self.testapp.get('/like.html?title_id=1')
        self.assertEqual(response.body, 'Success')

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
        self.assertEqual(response.body, 'Success')
