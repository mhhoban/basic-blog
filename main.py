from google.appengine.ext import ndb
from cookie_hasher import encode_cookie, verify_cookie
from regform_checks import (all_fields_complete, valid_email_check, passwords_match_check, duplicate_email_check,
                            nom_de_plume_available)
from register import registration

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


class Register(Handler):
    def get(self):

        # start off assuming no arguments
        email = False
        errors = False

        if len(self.request.get('email')) > 0:
            email = self.request.get('email')

        if len(self.request.get('errors')) > 0:
            errors = self.request.get('errors')

        if email and errors:
            self.render('registration_page.html', email=email, error=errors)

        elif errors:
            self.render('registration_page.html', error=errors)

        else:
            self.render('registration_page.html')

    def post(self):

        kwargs = self.request.POST

        self.render('registration_page.html', **kwargs)


class RegisterParse(Handler):

    def post(self):

        errors = ''

        fields = all_fields_complete(self.request.POST)

        if fields['fields_present'] is True:

            if valid_email_check(fields['email']):

                if nom_de_plume_available(fields['penname']):

                    if duplicate_email_check(fields['email']):

                        if passwords_match_check(fields['password'], fields['password_rep']):

                            registration(fields['email'], fields['password'],
                                         fields['penname'])

                            self.write('registration complete!')

                        else:

                            errors = 'mismatched_passwords'

                    else:
                        errors = 'duplicate_email'

                else:
                    errors = 'nom de plume taken'

            else:

                errors = 'invalid_email'

        else:

            errors = 'incomplete'

        if len(errors) > 0:

            self.redirect('/register.html?email='+fields['email']+'&errors='+errors)


# class Cookie_baker(Handler):
#     def get(self):
#         self.response.headers['Content-Type'] = 'text/plain'
#         self.response.headers.add_header('Set-Cookie', 'user-id-test=John Doe')
#         self.write("Cookie Set!")


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

        # hashed_cookie = 'test-hash' + ',' + encode_cookie()
        # self.response.headers.add_header('Set-Cookie', 'hashed-cookie='+hashed_cookie)

        self.render('front_page.html', user=user_id)

    def post(self):
        self.response.out.write("bar")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register.html', Register),
    ('/registration-parse.html', RegisterParse)
    ], debug=True)
