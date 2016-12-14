from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, LoginParse, LoginPage, BlogComposePage
from register import registration, delete_registration
from regform_checks import duplicate_email_check, nom_de_plume_available
from cookie_hasher import encode_cookie, verify_cookie
from blog_post_tools import blog_data_parser, store_post, get_all_posts

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from db_schema import Post


class Thing(ndb.Model):
    """ Models a Thing called THING!!!!"""

    name = ndb.StringProperty()


class Descendant_of_Thing(ndb.Model):
    """Models a descendant of THING!!!!"""

    name = ndb.StringProperty()


class DbTests(unittest.TestCase):

    def setUp(self):
        app = webapp2.WSGIApplication([('/', MainPage),
                                       ('/register.html', Register),
                                       ('/login.html', LoginPage),
                                       ('/blog-compose.html', BlogComposePage),
                                       ('/login-parse.html', LoginParse),
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
        #ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()

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

    def testRegistrationPage(self):
        """
        tests behavior of registration page
        :return:
        """
        response = self.testapp.get('/register.html')
        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('Register For Basic Blog!'))

    def testRegistrationNoPenNameorPassword(self):

        # test that function can handle incomplete form correctly
        response = self.testapp.post('/register.html', {'email': 'thing@thing.thing'})

        self.assertEqual(response.status_int, 200)
        assert_that(response.body, contains_string('incomplete'))
        assert_that(response.body, contains_string('thing@thing.thing'))

    def testRegistrationNoPenName(self):

        # test that function can handle incomplete form correctly
        response = self.testapp.post('/register.html', {'email': 'thing@thing.thing',
                                                                  'password': 'thing',
                                                                  'password_rep': 'thing',
                                                                  })

        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('incomplete'))

    def testRegistrationInvalidEmail(self):

        # test that registration-parse detects invalid email
        response = self.testapp.post('/register.html', {'email': 'thing',
                                                                  'password': 'thing',
                                                                  'password_rep': 'thing',
                                                                  'penname': 'thing'
                                                                  })

        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('thing'))
        assert_that(response.body, contains_string('invalid_email'))

    def testRegistrationPasswordMismatch(self):

        # test that registration-parse detects mismatched passwords in form

        response = self.testapp.post('/register.html', {'email': 'thing@thing.thing',
                                                                  'password': 'thing',
                                                                  'password_rep': 'things',
                                                                  'penname': 'thing',
                                                                  })

        self.assertEqual(response.status_int, 200)

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('mismatched_passwords'))

    def testDuplicateEmailCheck(self):

        registration('thing@thing', 'secret', 'thing')

        self.assertEqual(duplicate_email_check('thing@thingz'), True, 'False positive detecting duplicate emails')
        self.assertEqual(duplicate_email_check('thing@thing'), False, 'Not detecting duplicate email addresses')

        delete_registration('thing@thing')

    def testDuplicatePenName(self):

        registration('thing@thing', 'secret', 'thing')

        self.assertEqual(nom_de_plume_available('thingz'), True, 'False positive detecting duplicate pennames')
        self.assertEqual(nom_de_plume_available('thing'), False, 'Not detecting duplicate pennames')

        delete_registration('thing@thing')

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

        response = self.testapp.post('/login-parse.html', {'user_id': 'thing@thing.thing'})

        self.assertEqual(response.status_int, 302)

        assert_that(response.headers['Location'], contains_string('/login.html?error=incomplete'))

        response = self.testapp.get('/login.html?error=incomplete')

        assert_that(response.body, contains_string('incomplete'))

    def testInvalidEmail(self):

        response = self.testapp.post('/login-parse.html', {'user_id': 'thingz@thing.thing', 'password': 'blarg'})

        self.assertEqual(response.status_int, 302)

        assert_that(response.headers['Location'], contains_string('/login.html?error=invalid'))

        response = self.testapp.get('/login.html?error=invalid')

        assert_that(response.body, contains_string('invalid'))

    def testIncorrectPassword(self):

        registration('thing@thing', 'secret', 'thing')

        response = self.testapp.post('/login-parse.html', {'user_id': 'thing@thing', 'password': 'secretz'})

        self.assertEqual(response.status_int, 302)

        assert_that(response.headers['Location'], contains_string('/login.html?error=invalid'))

        response = self.testapp.get('/login.html?error=invalid')

        assert_that(response.body, contains_string('invalid'))

    def testValidLogin(self):

        registration('thingz@thingz', 'secret', 'thingz')

        response = self.testapp.post('/login-parse.html', {'user_id': 'thingz@thingz', 'password': 'secret'})

        self.assertEqual(response.status_int, 302)

        assert_that(response.headers['Location'], contains_string('/'))

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('thingz'))

    def testFrontPageNoPosts(self):

        response = self.testapp.get('/')

        assert_that(response.body, contains_string('No Posts Yet!'))

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

    # @unittest.expectedFailure
    def testBlogComposeParse(self):
        registration('test@user', 'secret', 'testuser')
        hashed_cookie = encode_cookie('test@user')
        self.testapp.set_cookie('user-id', hashed_cookie)

        response = self.testapp.post('/blog-compose.html', {'title': 'thing_title', 'content': 'thing_content'})
        self.assertEqual(response.status_int, 302)
        response = self.testapp.get('/')
        assert_that(response.body, contains_string('thing_title'))
        assert_that(response.body, contains_string('thing_content'))

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
        


if __name__ == '__main__':
    unittest.main()
