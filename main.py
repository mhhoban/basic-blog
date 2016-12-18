from auth_tools import auth_user
from hasher import encode_cookie
from regform_checks import (all_fields_complete, valid_email_check, passwords_match_check, duplicate_email_check,
                            nom_de_plume_available)
from login_checks import login_fields_complete, valid_user_id_check
from user_tools import check_password
from blog_post_tools import get_all_posts, store_post
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
    """
    Handles displaying registration page and parsing registration input
    """
    def get(self):
        """
        serves registration page

        """

        self.render('registration_page.html')

    def post(self):
        """
        parses data from reg page form and reloads page with data populated if there was an issue
        with the user input
        :return:
        """

        errors = ''

        fields = all_fields_complete(self.request.POST)

        if fields['fields_present'] is True:
            email = fields['email']
            errors = ''
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

            try:
                email = fields['email']
            except KeyError:
                email = ''

            errors = 'incomplete'

        if len(errors) > 0:

            self.render('registration_page.html', email=email, error=errors)


class LoginPage(Handler):
    """
    Displays LoginPage and parses login data
    """
    def get(self):
        """
        Displays Login Page for direct URL requests
        """

        self.render('login_page.html', error=False)

    def post(self):
        """
        Parses login data from form and reloads login-page if there is an issue with user input
        """

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
                    self.render('login_page.html', error='invalid')

            else:
                self.render('login_page.html', error='invalid')

        else:
            self.render('login_page.html', error='incomplete')


class BlogComposePage(Handler):
    """
    Serves blog compose page and parses blog compose data
    """
    def get(self):
        """
        serves the blog compose page for a new post
        """

        auth_check = auth_user(self)

        if auth_check['authorized']:

            self.render('blog_compose_page.html')

        else:

            self.redirect('/')

    def post(self):
        """
        parses blog compose data and reloads page if there is an issue with the blog
        submission data.
        """

        auth_check = auth_user(self)

        # import pdb
        # pdb.set_trace()

        if auth_check['authorized']:

            blog_data = self.request.POST
            blog_data['author'] = 'test_author'
            transaction_success = store_post(blog_data)

            if transaction_success:
                self.redirect('/')

            else:
                self.render('blog_compose_page.html', title=blog_data['title'], content=blog_data['content'])

        else:
            self.redirect('/')


class MainPage(Handler):
    """
    Displays index page
    """
    def get(self):

        # new determine if a visitor is logged in:

        auth_check = auth_user(self)

        if auth_check['authorized']:
            penname = auth_check['penname']

        else:
            penname = 'None'

        # get blog posts for display
        # TODO reverse chronological order
        posts = get_all_posts()

        self.render('front_page.html', user=penname, posts=posts)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register.html', Register),
    ('/login.html', LoginPage),
    ('/blog-compose.html', BlogComposePage),
    ], debug=True)
