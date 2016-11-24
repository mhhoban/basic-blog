from hamcrest import assert_that, contains_string

import unittest
import webapp2
import webtest

from main import Cookie_baker, MainPage, Register, RegisterParse
from regform_checks import duplicate_email_check

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
                                       ('/cookie', Cookie_baker)])
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

    def testThing(self):

        a_thing = Thing(name='THINGGG')
        a_thing.key = ndb.Key('Thing', 'bert')
        a_thing.put()

        b = a_thing.key.get()
        assert b.name == 'THINGGG'

    def testUser(self):

        a_user = Users(email='blarg@blarg.blarg', password='blargz')
        a_user.key = ndb.Key('Users', a_user.email)
        a_user.put()

        b_user = Users(email='blargz@blarg.blarg', password='blargzzz')
        b_user.key = ndb.Key('Users', b_user.email)
        b_user.put()

        # query = Users.query(Users.email == 'blah')

        query = Users.query()

        for user in query:
            print ndb.Key('Users', user.email)

    def testDuplicateEmailCheck(self):

        a_user = Users(email='thing@thing', password='secret')
        a_user.put()

        query = Users.query()

        print 'thing count:'
        print len(query.fetch())

        duplicate = duplicate_email_check('thing@thingz')

        assert duplicate


if __name__ == '__main__':
    unittest.main()
