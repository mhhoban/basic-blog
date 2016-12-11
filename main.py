from auth_tools import auth_user
from cookie_hasher import encode_cookie, verify_cookie
from regform_checks import (all_fields_complete, valid_email_check, passwords_match_check, duplicate_email_check,
                            nom_de_plume_available)
from login_checks import login_fields_complete, valid_user_id_check
from user_tools import fetch_penname, check_password
from blog_post_tools import get_all_posts, store_post
from register import registration
from google.appengine.ext import ndb


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


class TestUser(ndb.Model):
    name = ndb.StringProperty()


class TestUserPage(Handler):

    def get(self):

        test_user_num = TestUser.query()

        if test_user_num.count() < 1:
            self.write('started with no users ')

        a = TestUser(name='a')
        a.put()

        import time
        time.sleep(2)

        test_user_num = TestUser.query()

        if test_user_num.count() < 1:
            self.write('somehow ended with no users ' + str(test_user_num.count()))

        else:
            self.write('successfully added a user')
        b = TestUser(name='b')
        c = TestUser(name='c')

        # a.put()
        # b.put()
        # c.put()


class BlogComposeParse(Handler):

    def post(self):

        auth_check = auth_user(self)

        # import pdb
        # pdb.set_trace()

        if auth_check['authorized']:

            blog_data = self.request.POST
            blog_data['author'] = 'test_author'
            transaction_success = store_post(blog_data)
            if transaction_success:
                self.write('blog storage success')
            else:
                self.write('blog storage failure')

        else:
            self.redirect('/')


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

                            # TODO replace with single 'login' function

                            user_hash = encode_cookie(fields['email'])
                            self.response.set_cookie('user-id', str(user_hash))
                            self.redirect('/')

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


class LoginParse(Handler):
    def post(self):

        # import pdb
        # pdb.set_trace()

        login_parse = login_fields_complete(self.request.POST)

        if login_parse['complete']:

            valid_user_id = valid_user_id_check(login_parse['user_id'])

            if valid_user_id:

                correct_password = check_password(login_parse['user_id'], login_parse['password'])

                if correct_password:
                    # login
                    user_hash = encode_cookie(login_parse['user_id'])
                    self.response.set_cookie('user-id', str(user_hash))
                    self.redirect('/')

                else:
                    self.redirect('/login.html?error=invalid')

            else:
                self.redirect('/login.html?error=invalid')

        else:
            self.redirect('/login.html?error=incomplete')


class LoginPage(Handler):
    def get(self):

        if len(self.request.get('error')) > 0:
            error = self.request.get('error')

        else:
            error = False

        self.render('login_page.html', error=error)


class BlogComposePage(Handler):
    def get(self):

        auth_check = auth_user(self)

        if auth_check['authorized']:

            self.render('blog_compose_page.html')

        else:

            self.redirect('/')


class MainPage(Handler):
    def get(self):

        # new determine if a visitor is logged in:

        auth_check = auth_user(self)

        # import pdb
        # pdb.set_trace()

        if auth_check['authorized']:
            penname = auth_check['penname']

        else:
            penname = 'None'

        # get blog posts for display
        posts = get_all_posts()

        self.render('front_page.html', user=penname, posts=posts)

    def post(self):
        self.response.out.write("bar")

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register.html', Register),
    ('/registration-parse.html', RegisterParse),
    ('/login-parse.html', LoginParse),
    ('/login.html', LoginPage),
    ('/test-key', TestUserPage),
    ('/blog-compose.html', BlogComposePage),
    ('/blog-compose-parse.html', BlogComposeParse),
    ], debug=True)
