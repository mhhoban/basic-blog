from auth_tools import auth_user
from hasher import encode_cookie
from regform_checks import (all_fields_complete, valid_email_check, passwords_match_check, duplicate_email_check,
                            nom_de_plume_available)
from login_checks import login_fields_complete, valid_user_id_check
from user_tools import check_password
from blog_post_tools import (get_all_posts, store_post, get_post_author, get_post_data, get_post_comment_total,
                             update_post, get_post_likes, add_post_like, add_comment, get_post_comments,
                             get_comment_author, get_comment_data, delete_comment, delete_post)
from register import registration
from time import sleep

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


class LogoutPage(Handler):
    """
    Logs out users
    """

    def get(self):

        auth_check = auth_user(self)

        if auth_check['authorized']:
            # destroy cookie
            self.response.delete_cookie('user-id')

            self.redirect('/')

        else:
            self.redirect('/')


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
            blog_data['author'] = auth_check['penname']
            transaction_success = store_post(blog_data)

            if transaction_success:
                self.redirect('/')

            else:
                self.render('blog_compose_page.html', title=blog_data['title'], content=blog_data['content'])

        else:
            self.redirect('/')


class BlogEditPage(Handler):
    """
    loads blog edit page and reloads page if there is an issue with the blog submission data
    """

    def auth_edit_post(self, blog_id, user_name):

        blog_author = get_post_author(blog_id)

        if blog_author == user_name:
            return True

        else:
            return False

    def get(self):

        auth_check = auth_user(self)

        if auth_check['authorized']:
            user_name = auth_check['penname']
            blog_id = long(self.request.GET['blog_id'])

            if self.auth_edit_post(blog_id, user_name):

                post_data = get_post_data(blog_id)

                self.render('blog_edit_page.html', content=post_data.content, title=post_data.title,
                            blog_id=blog_id)

            else:
                self.write('Not Authorized to Edit Post')

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
            blog_data['author'] = auth_check['penname']
            transaction_success = update_post(blog_data)

            if transaction_success:
                self.write('Blog Updated Successfully!')
                sleep(1)
                self.redirect('/')

            else:
                self.render('blog_edit_page.html', title=blog_data['title'], content=blog_data['content'],
                            blog_id=blog_data['blog_id'])

        else:
            self.redirect('/')


class DeletePost(Handler):

    def get(self):
        auth_check = auth_user(self)

        if auth_check['authorized']:

            blog_id = long(self.request.GET['blog_id'])
            blog_author = get_post_author(blog_id)

            if auth_check['penname'] == blog_author:
                post_data = get_post_data(blog_id)

                self.render('delete_post.html',
                            user=auth_check['penname'],
                            content=post_data.content,
                            title=post_data.title,
                            author=post_data.author,
                            blog_id=blog_id)

            else:
                self.redirect('/')

        else:
            self.redirect('/')

    def post(self):

        auth_check = auth_user(self)

        if auth_check['authorized']:

            blog_id = long(self.request.POST['blog_id'])
            blog_author = get_post_author(blog_id)

            if auth_check['penname'] == blog_author:
                post_data = get_post_data(blog_id)

                if delete_post(blog_id):
                    self.redirect('/')

            else:
                self.redirect('/')

        else:
            self.redirect('/')


class ViewPost(Handler):
    def get(self):

        blog_id = long(self.request.GET['blog_id'])
        post_data = get_post_data(blog_id)

        # load and parse comments:
        comments = get_post_comments(blog_id)

        auth_check = auth_user(self)

        if auth_check['authorized']:

            # check if visitor is allowed to edit:
            if post_data.author == auth_check['penname']:
                can_comment = False

            else:
                can_comment = True

            self.render('blog_view_page_authed.html',
                        user=auth_check['penname'],
                        content=post_data.content,
                        title=post_data.title,
                        author=post_data.author,
                        comments=comments,
                        can_comment=can_comment,
                        blog_id=blog_id)

        else:

            self.render('blog_view_page_non_authed.html',
                        content=post_data.content,
                        title=post_data.title,
                        blog_id=blog_id,
                        author=post_data.author)


class LikePost(Handler):
    def get(self):

        auth_check = auth_user(self)

        if auth_check['authorized']:

            title_id = long(self.request.get('title_id'))

            if get_post_data(title_id):

                post_author = get_post_author(title_id)
                current_user = auth_check['penname']

                if post_author != current_user:

                    likes = get_post_likes(title_id)

                    try:
                        test_author = likes[current_user]
                        self.write('already liked')

                    except KeyError:
                        if add_post_like(title_id, current_user):
                            self.write('Success')

                else:
                    self.write('cannot like own post')

            else:
                self.write('no such post')

        else:
            self.redirect('/')


class AddComment(Handler):

    def post(self):
        auth_check = auth_user(self)

        if auth_check['authorized']:

            title_id = long(self.request.POST['title_id'])
            comment_content = self.request.POST['comment']

            if get_post_data(title_id):

                post_author = get_post_author(title_id)
                current_user = auth_check['penname']

                if post_author != current_user:

                    if add_comment(title_id, current_user, comment_content):
                        self.render('comment.html', result='success')
                        sleep(3)
                        self.redirect('/')

                    else:

                        render('comment.html', result='failure')

                else:
                    self.write('cannot comment on own post')

            else:
                self.write('No Such Post')

        else:
            self.redirect('/')


class DeleteComment(Handler):

    def get(self):
        auth_check = auth_user(self)

        if auth_check['authorized']:

            blog_id = long(self.request.GET['blog_id'])
            comment_id = self.request.GET['comment_id']
            commenter = get_comment_author(blog_id, comment_id)

            if commenter == auth_check['penname']:

                post_data = get_post_data(blog_id)
                comment = get_comment_data(blog_id, comment_id)

                self.render('/delete_comment.html',
                            user=auth_check['penname'],
                            content=post_data.content,
                            title=post_data.title,
                            author=post_data.author,
                            comment=comment,
                            comment_id=comment_id,
                            blog_id=blog_id)

            else:
                self.redirect('/')

        else:
            self.redirect('/')

    def post(self):
        auth_check = auth_user(self)

        if auth_check['authorized']:

            blog_id = long(self.request.POST['blog_id'])
            comment_id = self.request.POST['comment_id']
            commenter = get_comment_author(blog_id, comment_id)

            if commenter == auth_check['penname']:

                if delete_comment(blog_id, comment_id):
                    self.redirect('/view?blog_id='+str(blog_id))

            else:
                self.redirect('/')

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

            # get blog posts for display
            # TODO reverse chronological order
            entries = get_all_posts()

            posts = []

            penname = auth_check['penname']

            for entry in entries:
                view_mode = 'like'
                if entry.author == penname:
                    view_mode = 'edit'

                likes = get_post_likes(entry.key.id())
                post_likes = ''
                if len(likes) < 1:
                    post_likes = 'No Likes Yet!'

                else:
                    post_likes = 'This post is liked by:'
                    for like in likes.keys():
                        if like == penname:
                            view_mode = 'liked'
                        post_likes = post_likes + ' ' + like + ','

                posts.append({'title': entry.title,
                              'id': entry.key.id(),
                              'author': entry.author,
                              'content': entry.content,
                              'likes': post_likes,
                              'view_mode': view_mode,
                              'comment_total': get_post_comment_total(entry.key.id()),
                              })

            self.render('front_page_authed.html', user=penname, posts=posts)

        else:

            # get blog posts for display
            # TODO reverse chronological order
            entries = get_all_posts()

            posts = []

            for entry in entries:

                likes = get_post_likes(entry.key.id())
                post_likes = ''
                if len(likes) < 1:
                    post_likes = 'No Likes Yet!'

                else:
                    post_likes = 'This post is liked by:'
                    for like in likes.keys():
                        post_likes = post_likes + ' ' + like + ','

                posts.append({'title': entry.title,
                              'id': entry.key.id(),
                              'author': entry.author,
                              'content': entry.content,
                              'likes': post_likes,
                              'comment_total': get_post_comment_total(entry.key.id()),
                              })

            self.render('front_page_non_authed.html', posts=posts)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register.html', Register),
    ('/login.html', LoginPage),
    ('/blog-compose.html', BlogComposePage),
    ('/blog-edit.html', BlogEditPage),
    ('/logout.html', LogoutPage),
    ('/like.html', LikePost),
    ('/view.html', ViewPost),
    ('/comment.html', AddComment),
    ('/delete_comment.html', DeleteComment),
    ('/delete-post.html', DeletePost)
    ], debug=True)
