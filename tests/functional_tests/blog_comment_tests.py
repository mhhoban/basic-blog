from selenium import webdriver
from hamcrest import assert_that, contains_string, is_not
from time import sleep

from selenium.common.exceptions import NoSuchElementException

from auto_tools import AppServer, AutoTestTools

import unittest


class CommentTests(unittest.TestCase):

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

    def test_blog_comment(self):

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

    def test_comment_button_total(self):

        tools = AutoTestTools()

        tools.gen_post_alpha()
        reg_b = tools.register_user_beta()
        self.assertTrue(reg_b, 'could not register user b')
        tools.gen_post_alpha()

        self.browser.get('http://localhost:8080')

        sleep(3)

        tools.log_in_user(self.browser, 'a@a.b', 'thing')

        sleep(2)

        tools.view_post(self.browser)

        sleep(2)

        tools.make_comment_alpha(self.browser)

        try:
            comment_button = self.browser.find_element_by_id('comment_total_button')

        except NoSuchElementException:
            comment_button = False

        self.assertTrue(comment_button, 'could not find comment button')

        comment_total = int(comment_button.text)

        self.assertEqual(comment_total, 2)

