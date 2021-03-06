from blog_post_tools import (add_comment, blog_data_parser, delete_comment, delete_post, get_all_posts,
                             get_post_author, get_post_data, store_post, update_post)
from db_schema import Post
from google.appengine.ext import ndb, testbed
from hamcrest import assert_that, contains_string, equal_to
from hasher import encode_cookie
from main import MainPage, Register, LoginPage, BlogComposePage, BlogEditPage
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

    def testFrontPageNoPosts(self):

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('Register and make the first post to replace me!'))

    def testComposePostLinkLoggedIn(self):
        """
        ensure blog compose link is present for those signed in
        :return:
        """
        registration('thingz@thingz', 'secret', 'thingz')

        response = self.testapp.post('/login.html', {'login-choice': 'login', 'user_id': 'thingz@thingz',
                                                     'password': 'secret'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('/'))
        response = self.testapp.get('/')

        assert_that(response.body, contains_string('thingz'))
        assert_that(response.body, contains_string('Compose Post'))

    def testComposePostLinkNotLoggedIn(self):
        """
        ensure blog compose link is not present for those not signed in
        :return:
        """

        response = self.testapp.get('/')

        try:
            assert_that(response.body, contains_string(
                '<a href = "blog-compose.html" > Compose Post </a>')
                        )
            link_present = True

        except AssertionError:
            link_present = False

        self.assertFalse(link_present)

    def testComposePostLinkWorks(self):

        registration('thingz@thingz', 'secret', 'thingz')

        response = self.testapp.post('/login.html', {'login-choice': 'login', 'user_id': 'thingz@thingz',
                                                     'password': 'secret'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('/'))
        response = self.testapp.get('/')

        assert_that(response.body, contains_string('thingz'))
        assert_that(response.body, contains_string('Compose Post'))

        response = self.testapp.get('/blog-compose.html')

        self.assertEqual(response.status_int, 200)
        assert_that(response.body, contains_string('Compose Your Blog Post!'))

    def testPostDataParsing(self):

        data = blog_data_parser({'title': 'thing_title', 'content': 'thing_content', 'author': 'thing_author'})

        self.assertEqual(data['valid'], True)
        self.assertEqual(data['title'], 'thing_title')
        self.assertEqual(data['content'], 'thing_content')
        self.assertEqual(data['author'], 'thing_author')

    def testComposePostWorks(self):

        data = store_post({'title': 'thing_title', 'content': 'thing_content', 'author': 'thing_author'})
        self.assertEqual(data, True)

    def testRetrieveAllPostsWorks(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'thingz_author'})
        self.assertEqual(data, True)
        data = get_all_posts()
        self.assertEqual(data[0].title, 'thingz_title')
        self.assertEqual(data[0].content, 'thingz_content')
        self.assertEqual(data[0].author, 'thingz_author')

    def testPostsLoadOnFrontPage(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'thingz_author'})
        data = store_post({'title': 'thingz_atitle', 'content': 'thingz_acontent', 'author': 'thingz_aauthor'})
        self.assertEqual(data, True)
        response = self.testapp.get('/')
        assert_that(response.body, contains_string('thingz_title'))
        assert_that(response.body, contains_string('thingz_author'))
        assert_that(response.body, contains_string('thingz_content'))
        assert_that(response.body, contains_string('thingz_atitle'))
        assert_that(response.body, contains_string('thingz_aauthor'))
        assert_that(response.body, contains_string('thingz_acontent'))

    def testBlogComposeParse(self):
        registration('test@user', 'secret', 'testuser')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

        response = self.testapp.post('/blog-compose.html', {'title': 'thing_title', 'content': 'thing_content'})
        self.assertEqual(response.status_int, 302)
        response = self.testapp.get('/')
        assert_that(response.body, contains_string('thing_title'))
        assert_that(response.body, contains_string('thing_content'))

    def testGetBlogPostAuthor(self):
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'thingz_author'})

        if data:
            blog_data = Post.query().fetch()

            blog_id = blog_data[0].key.id()

            blog_author = get_post_author(blog_id)

            self.assertEqual(blog_author, 'thingz_author')

    def testGetBlogData(self):

        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'thingz_author'})

        if data:

            blog_data = get_post_data(long(1))

            self.assertEqual(blog_data.title, 'thingz_title')

    def testBlogPostUpdateAuth(self):
        registration('test@user', 'secret', 'testuser')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)
        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        response = self.testapp.get('/blog-edit.html?blog_id=1')
        self.assertEqual(response.status_int, 200)
        self.assertEqual(response.body, 'Not Authorized to Edit Post')

    def testBlogPostUpdate(self):

        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        self.assertEqual(test_post.content, 'thingz_content')

        data = update_post({'blog_id': 1, 'title': 'thingz_title', 'content': 'thingzzzz'})

        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        self.assertEqual(test_post.content, 'thingzzzz')

    def testBlogPostCommentDeletion(self):

        registration('testa@user', 'secret', 'testusera')
        registration('testb@user', 'secret', 'testuserb')
        hashed_cookie = encode_cookie('testa@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})
        data = add_comment(1, 'testuberb', 'blargz')

        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        comments = test_post.comments
        comments = json.loads(comments)
        assert_that(len(comments), equal_to(1), 'test comment not being written')
        comment_id = comments[0]['comment_id']

        delete_comment(1, comment_id)
        test_post_key = ndb.Key('Post', 1)
        test_post = test_post_key.get()
        comments = test_post.comments
        comments = json.loads(comments)

        assert_that(len(comments), equal_to(0), 'test comment not being deleted')

    def testBlogPostDeletion(self):

        data = store_post({'title': 'thingz_title', 'content': 'thingz_content', 'author': 'testuserz'})

        delete_post(1)

        target_post_key = ndb.Key('Post', 1)

        self.assertEqual(target_post_key.get(), None, 'Post Not Deleted')
