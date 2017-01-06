import subprocess
import requests
from selenium.common.exceptions import NoSuchElementException
import os
import signal
from hasher import encode_cookie
from hamcrest import assert_that, contains_string, is_not


class AutoTestTools():

    def register_user_alpha(self):

        reg_response = requests.post('http://localhost:8080/register.html',
                                     data={'email': 'a@a.a',
                                                    'password': 'thing',
                                                    'password_rep': 'thing',
                                                    'penname': 'thinga'
                                           },
                                     )

        if 'thinga' in reg_response.content:
            reg = True

        else:
            reg = False

        return reg

    def register_user_beta(self):

        reg_response = requests.post('http://localhost:8080/register.html',
                                     data={'email': 'a@a.b',
                                           'password': 'thing',
                                           'password_rep': 'thing',
                                           'penname': 'thingb'
                                           },
                                     )

        if 'thingb' in reg_response.content:
            reg = True

        else:
            reg = False

        return reg

    def gen_post_alpha(self):

        hashed_cookie = encode_cookie('a@a.a')
        response = requests.post('http://localhost:8080/blog-compose.html',
                                 cookies={'user-id': hashed_cookie},
                                 data={'title': 'Generic Post of A',
                                       'content': 'Generic general first post of A',
                                       'author': 'thinga',
                                       },
                                 )
        if 'Generic Post of A' in response.content:

            post = True

        else:

            post = False

        return post

    def view_post(self, browser):

        try:
            read_more_link = browser.find_element_by_link_text("Read More")

        except NoSuchElementException:
            read_more_link = False

        assert_that(read_more_link, is_not(False), 'Could Not find read more button')

        read_more_link.click()

    def make_comment_alpha(self, browser):

        try:
            comment_field = browser.find_element_by_name('comment')

        except NoSuchElementException:
            comment_field = False

        assert_that(comment_field, is_not(False), 'comment_field not detected')

        try:
            comment_button = browser.find_element_by_name('comment_button')

        except NoSuchElementException:
            comment_button = False

        assert_that(comment_button, is_not(False), 'comment_button not detected')

        comment_field.send_keys('testing of the comment field')

        comment_button.click()

    def log_in_user(self, browser, user_id, password):

        # Then sees a field for an email input
        try:
            email_field = browser.find_element_by_id('user_id')

        except NoSuchElementException:
            email_field = False

        assert_that(email_field, is_not(False), 'email_field not detected for non-logged in user')

        # Then sees a field for a password input
        try:
            password_field = browser.find_element_by_id('password')

        except NoSuchElementException:
            password_field = False

        assert_that(password_field, is_not(False), 'password_field not detected for non-logged in user')

        # Then sees a login button
        try:
            login_button = browser.find_element_by_name('login-submit')

        except NoSuchElementException:
            login_button = False

        assert_that(login_button, is_not(False), 'login button not detected for non-logged in user')

        # ------------------------ Try Logging in as user

        email_field.send_keys(user_id)
        password_field.send_keys(password)

        login_button.click()


class AppServer:

    def __init__(self):
        self.server = None

    def start_server(self):

        # wipe old test data:
        try:
            subprocess.Popen(['rm temp/myapp_test_datastore'], shell=True)

        except KeyboardInterrupt:
            print 'No test data file to delete'

        self.server = subprocess.Popen(['dev_appserver.py --datastore_path=temp/myapp_test_datastore .'], shell=True)

    def stop_app_server(self):

        os.kill(self.server.pid, signal.SIGINT)