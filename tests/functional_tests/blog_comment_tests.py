from selenium import webdriver
from hamcrest import assert_that, contains_string, is_not
from time import sleep
from hasher import encode_cookie

from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import unittest
import subprocess
import os
import signal
import requests

# caps['marionette'] = True


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


class SignupTests(unittest.TestCase):

    def setUp(self):

        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument("--incognito")

        self.browser = webdriver.Chrome(chrome_options=chrome_opts)
        self.browser.set_window_size(1300, 1300)
        self.test_server = AppServer()
        self.test_server.start_server()
        sleep(3)

    def tearDown(self):
        self.browser.quit()
        self.test_server.stop_app_server()

    def test_blog_comments(self):

        # test setup
        tools = AutoTestTools()
        reg_a = tools.register_user_alpha()
        self.assertTrue(reg_a, 'could not register user a')
        reg_b = tools.register_user_beta()
        self.assertTrue(reg_b, 'could not register user b')
        tools.gen_post_alpha()

        # User visits the blog, which loads successfully
        self.browser.get('http://localhost:8080')

        sleep(3)

        tools.log_in_user(self.browser, 'a@a.b', 'thing')

        sleep(2)

        tools.view_post(self.browser)

        sleep(2)

        tools.make_comment_alpha(self.browser)

        sleep(2)

        tools.view_post(self.browser)

        sleep(2)

        try:
            comment = self.browser.find_element_by_id('comment')

        except NoSuchElementException:
            comment = False

        assert_that(comment, is_not(False), 'could not find comment after commenting')

        assert_that(comment.text, contains_string('testing of the comment field'),
                    'comment content incorrect')

    def test_comment_on_own_post(self):

        # test set-up
        tools = AutoTestTools()
        reg_a = tools.register_user_alpha()
        self.assertTrue(reg_a, 'could not register user a')
        reg_b = tools.register_user_beta()
        self.assertTrue(reg_b, 'could not register user b')
        tools.gen_post_alpha()

        # User visits the blog, which loads successfully
        self.browser.get('http://localhost:8080')

        sleep(3)

        # log in as same user that has posted
        tools.log_in_user(self.browser, 'a@a.a', 'thing')

        sleep(2)

        tools.view_post(self.browser)

        sleep(2)

        try:
            comment_button = self.browser.find_element_by_id('add-comment-button')

        except NoSuchElementException:
            comment_button = False

        self.assertFalse(comment_button, 'user able to comment on their own post')


if __name__ == '__main__':
    unittest.main()
