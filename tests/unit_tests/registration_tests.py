from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import MainPage, Register, LoginPage, BlogComposePage
from register import registration, delete_registration
from regform_checks import duplicate_email_check, nom_de_plume_available

from google.appengine.ext import testbed


class RegTests(unittest.TestCase):

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
