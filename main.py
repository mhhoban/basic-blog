from google.appengine.ext import ndb
from cookie_hasher import encode_cookie, verify_cookie

import os
import jinja2
import webapp2


template_dir = os.path.join(os.path.dirname(__file__), 'templates')

JINJA_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))


class Handler(webapp2.RequestHandler):
    """Handles templating requests"""

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = JINJA_ENV.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Thing(ndb.Model):
    """ Models a Thing called THING!!!!"""

    name = ndb.StringProperty()


class Descendant_of_Thing(ndb.Model):
    """Models a descendant of THING!!!!"""

    name = ndb.StringProperty()


class Cookie_baker(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers.add_header('Set-Cookie', 'user-id-test=John Doe')
        self.write("Cookie Set!")


class MainPage(Handler):
    def get(self):

        # a_thing = Thing(name='THINGGG')
        # a_thing.key = ndb.Key('Thing', 'bert')
        # a_thing.put()
        #
        # b = a_thing.key.get()

        # self.response.headers['Content-Type'] = 'text/plain'

        user_hash = self.request.cookies.get('user-id', 'None')
        user_id = 'None'

        if user_hash != 'None':
            hashed_login = user_hash.split(',')
            if verify_cookie(hashed_login):
                user_id = hashed_login[0]

        hashed_cookie = 'test-hash' + ',' + encode_cookie()
        # self.response.headers.add_header('Set-Cookie', 'hashed-cookie='+hashed_cookie)

        self.render('front_page.html', user=user_id)

    def post(self):
        self.response.out.write("bar")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/cookie.html', Cookie_baker),
    ], debug=True)
