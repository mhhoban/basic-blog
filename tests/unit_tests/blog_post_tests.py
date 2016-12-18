from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, LoginPage, BlogComposePage
from register import registration
from hasher import encode_cookie
from blog_post_tools import blog_data_parser, store_post, get_all_posts

from google.appengine.ext import testbed


class BlogPostTests(unittest.TestCase):

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

    def testFrontPageNoPosts(self):

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('No Posts Yet!'))

    def testComposePostLinkLoggedIn(self):
        registration('thingz@thingz', 'secret', 'thingz')

        response = self.testapp.post('/login.html', {'user_id': 'thingz@thingz', 'password': 'secret'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('/'))
        response = self.testapp.get('/')

        assert_that(response.body, contains_string('thingz'))
        assert_that(response.body, contains_string('Compose Post'))

    def testComposePostLinkNotLoggedIn(self):

        response = self.testapp.get('/')

        try:
            assert_that(response.body, contains_string(
                '<a href = "blog-compose.html" > Compose Post </a>')
                        )
            link_present = True

        except AssertionError:
            link_present = False

        self.assertFalse(link_present)

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