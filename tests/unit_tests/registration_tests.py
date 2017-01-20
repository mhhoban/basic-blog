from google.appengine.ext import ndb, testbed
from hamcrest import assert_that, contains_string
from main import BlogComposePage, LoginPage, MainPage, Register
from register import registration
from regform_checks import duplicate_email_check, nom_de_plume_available

import hmac
import unittest
import webapp2
import webtest


class RegTests(unittest.TestCase):

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

    def testDuplicatePenName(self):

        registration('thing@thing', 'secret', 'thing')

        self.assertEqual(nom_de_plume_available('thingz'), True, 'False positive detecting duplicate pennames')
        self.assertEqual(nom_de_plume_available('thing'), False, 'Not detecting duplicate pennames')

    def testPasswordHashing(self):

        registration('thing@thing', 'secret', 'thing')

        # hashing function:

        user_key = ndb.Key('User', 'thing@thing')
        user = user_key.get()
        hashed_password = user.password

        manual_hash = hmac.new('other-arbitrary-secret', 'secret').hexdigest()

        self.assertEqual(hashed_password, manual_hash)