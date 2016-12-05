from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, RegisterParse, LoginParse, LoginPage
from register import registration, delete_registration
from regform_checks import duplicate_email_check, nom_de_plume_available
from cookie_hasher import encode_cookie, verify_cookie

from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from db_schema import Users


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
                                       ('/registration-parse.html', RegisterParse),
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
        ndb.get_context().clear_cache()

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

    def testRegistrationConnection(self):
        """
        tests that the page that receives and processes signup input is working
        :return:
        """

        # test that route to registration-parse is working
        response = self.testapp.post('/registration-parse.html')
        assert response

    def testRegistrationNoPenNameorPassword(self):

        # test that function can handle incomplete form correctly
        response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing'})

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing@thing.thing' +
                                                                  '&errors=incomplete'))

        response = self.testapp.get('/register.html?email=thing@thing.thing&errors=incomplete')

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('incomplete'))

    def testRegistrationNoPenName(self):

        # test that function can handle incomplete form correctly
        response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing',
                                                                  'password': 'thing',
                                                                  'password_rep': 'thing',
                                                                  })

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing@thing.thing' +
                                                                  '&errors=incomplete'))

        response = self.testapp.get('/register.html?email=thing@thing.thing&errors=incomplete')

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('incomplete'))

    def testRegistrationInvalidEmail(self):

        # test that registration-parse detects invalid email
        response = self.testapp.post('/registration-parse.html', {'email': 'thing',
                                                                  'password': 'thing',
                                                                  'password_rep': 'thing',
                                                                  'penname': 'thing'
                                                                  })

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing' +
                                                                  '&errors=invalid_email'))

        response = self.testapp.get('/register.html?email=thing&errors=invalid_email')

        assert_that(response.body, contains_string('thing'))
        assert_that(response.body, contains_string('invalid_email'))

    def testRegistrationPasswordMisMatch(self):

        # test that registration-parse detects mismatched passwords in form

        response = self.testapp.post('/registration-parse.html', {'email': 'thing@thing.thing',
                                                                  'password': 'thing',
                                                                  'password_rep': 'things',
                                                                  'penname': 'thing',
                                                                  })

        self.assertEqual(response.status_int, 302)
        assert_that(response.headers['Location'], contains_string('register.html?email=thing@thing.thing' +
                                                                  '&errors=mismatched_passwords'))

        response = self.testapp.get('/register.html?email=thing@thing.thing&errors=mismatched_passwords')

        assert_that(response.body, contains_string('thing@thing.thing'))
        assert_that(response.body, contains_string('mismatched_passwords'))


    # def testThing(self):
    #
    #     a_thing = Thing(name='THINGGG')
    #     a_thing.key = ndb.Key('Thing', 'bert')
    #     a_thing.put()
    #
    #     b = a_thing.key.get()
    #     assert b.name == 'THINGGG'

    # def testUser(self):
    #
    #     a_user = Users(email='blarg@blarg.blarg', password='blargz')
    #     a_user.key = ndb.Key('Users', a_user.email)
    #     a_user.put()
    #
    #     b_user = Users(email='blargz@blarg.blarg', password='blargzzz')
    #     b_user.key = ndb.Key('Users', b_user.email)
    #     b_user.put()
    #
    #     # query = Users.query(Users.email == 'blah')
    #
    #     query = Users.query()
    #
    #     for user in query:
    #         print ndb.Key('Users', user.email)


    # def testCookieHashing(self):
    #     """
    #     tests that visiting the main page detects cookies appropriately
    #     :return:
    #     """
    #
    #     self.testapp.set_cookie('user-id', 'test-hash,420ad9ff2d6c88f4782ebbd7a4f03a82')
    #
    #     response = self.testapp.get('/')
    #     assert_that(response.body, contains_string('test-hash'))

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

        hashed_cookie = hashed_cookie.split(',')
        correct_hash = verify_cookie(hashed_cookie)

        self.assertEqual(correct_hash, True, 'False Negative on hash decoding')

        hashed_cookie = encode_cookie('thingz@thing')

        hashed_cookie = hashed_cookie.split(',')
        hashed_cookie[0] = 'blarg'

        correct_hash = verify_cookie(hashed_cookie)

        self.assertEqual(correct_hash, False, 'False positive on hash decoding')

    def testIncompleteLoginFields(self):

        response = self.testapp.post('/login-parse.html', {'user_id': 'thing@thing.thing'})

        assert_that(response.body, contains_string('really incomplete'))

    def testInvalidEmail(self):

        response = self.testapp.post('/login-parse.html', {'user_id': 'thingz@thing.thing', 'password': 'blarg'})

        assert_that(response.body, contains_string('invalid'))

    def testIncorrectPassword(self):

        registration('thing@thing', 'secret', 'thing')

        response = self.testapp.post('/login-parse.html', {'user_id': 'thing@thing', 'password': 'secretz'})

        assert_that(response.body, contains_string('wrong password'))

    def testValidLogin(self):
        #
        pass

    def testFrontPageNoPosts(self):

        response = self.testapp.get()

if __name__ == '__main__':
    unittest.main()
