from selenium import webdriver
from hamcrest import assert_that, contains_string
from time import sleep
from auto_tools import AppServer, AutoTestTools
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import unittest


class SignupTests(unittest.TestCase):

    def setUp(self):

        chrome_opts = webdriver.ChromeOptions()
        chrome_opts.add_argument("--incognito")

        self.browser = webdriver.Chrome(chrome_options=chrome_opts)
        self.browser.set_window_size(1300, 1300)

        self.test_server = AppServer()
        self.test_server.start_server()

        self.tools = AutoTestTools()

        sleep(3)

    def tearDown(self):
        self.browser.quit()
        self.test_server.stop_app_server()

    def test_compose_blog_post(self):

        self.tools = AutoTestTools()

        self.tools.register_user_alpha()

        self.browser.get('http://localhost:8080')

        sleep(2)

        self.tools.log_in_user(self.browser, 'a@a.a', 'thing')

        sleep(2)

        try:
            compose_link = self.browser.find_element_by_link_text('Compose Post')
        except NoSuchElementException:
            compose_link = False

        self.assertTrue(compose_link, 'compose blog link not found')

        compose_link.click()

        sleep(2)

        # ----------------------------------------------------------- Actually Compose Blog Post
        # confirm title field present:

        try:
            title_field = self.browser.find_element_by_xpath("//*/div[@class='blog-compose-title']/input")

        except NoSuchElementException:
            title_field = False

        self.assertTrue(title_field, 'Could not locate Blog Compose Title Field')

        try:
            content_field = self.browser.find_element_by_xpath("//*/div[@class='blog-compose-field']/textarea")

        except NoSuchElementException:
            content_field = False

        self.assertTrue(content_field, 'Could not locate Blog Compose Content')

        try:
            submit_button = self.browser.find_element_by_xpath("//*/div[@class='blog-compose-button']/button")

        except NoSuchElementException:
            submit_button = False

        self.assertTrue(submit_button, 'Could not locate Blog Compose Submit Button')

        # Compose the post
        title_field.send_keys('Test Blog Post A')
        content_field.send_keys('The Body of Blog Post A')

        # Hit submit
        submit_button.click()

        # ---------------------------------------------------------------- Confirm Blog Post Posted
        # confirm UI elements present:
        sleep(3)

        try:
            blog_title = self.browser.find_element_by_xpath("//*/div[@class='post-title']/h3")

        except NoSuchElementException:
            blog_title = False

        self.assertTrue(blog_title, 'Could not find Blog Title After posting')

        try:
            blog_author = self.browser.find_element_by_xpath("//*/div[@class='post-author']/h3")

        except NoSuchElementException:
            blog_author = False

        self.assertTrue(blog_author, 'Could not find Blog Author After posting')

        try:
            blog_content = self.browser.find_element_by_xpath("//*/div[@class='post-content']/p")

        except NoSuchElementException:
            blog_content = False

        self.assertTrue(blog_title, 'Could not find Blog content After posting')

        # confirm content is correct:
        self.assertEqual(blog_title.text, 'Test Blog Post A')
        self.assertEqual(blog_author.text, 'thinga')
        self.assertEqual(blog_content.text, 'Start Writing! The Body of Blog Post A')

    def test_blog_post_edit(self):

        self.tools.register_user_alpha()
        self.tools.gen_post_alpha()

        self.browser.get('http://localhost:8080')
        sleep(2)
        self.tools.log_in_user(self.browser, 'a@a.a', 'thing')
        sleep(2)

        try:
            edit_link = self.browser.find_element_by_link_text('Edit Post!')

        except NoSuchElementException:
            edit_link = False

        self.assertTrue(edit_link, 'Could not find Blog edit after posting')

        edit_link.click()

        # confirm page elements
        sleep(2)

        try:
            edit_title = self.browser.find_element_by_xpath("//*/div[@class='blog-compose-title']/input")

        except NoSuchElementException:
            edit_title = False

        self.assertTrue(edit_title, 'Could not find Blog edit title field')

        try:
            edit_content = self.browser.find_element_by_xpath("//*/div[@class='blog-compose-field']/textarea")

        except NoSuchElementException:
            edit_content = False

        self.assertTrue(edit_content, 'Could not find Blog edit content field')

        try:
            edit_button = self.browser.find_element_by_xpath("//*/div[@class='blog-compose-button']/button")

        except NoSuchElementException:
            edit_button = False

        self.assertTrue(edit_button, 'Could not find Blog edit button field')

        # -------------------------------------------------------------------- Edit Post

        edit_title.send_keys(' Edited')
        edit_content.send_keys(' Edited')
        edit_button.click()

        # -------------------------------------------------------------------- Confirm edit

        sleep(2)

        try:
            blog_title = self.browser.find_element_by_xpath("//*/div[@class='post-title']/h3")

        except NoSuchElementException:
            blog_title = False

        self.assertTrue(blog_title, 'Could not find Blog Title After posting')

        try:
            blog_author = self.browser.find_element_by_xpath("//*/div[@class='post-author']/h3")

        except NoSuchElementException:
            blog_author = False

        self.assertTrue(blog_author, 'Could not find Blog Author After posting')

        try:
            blog_content = self.browser.find_element_by_xpath("//*/div[@class='post-content']/p")

        except NoSuchElementException:
            blog_content = False

        self.assertTrue(blog_title, 'Could not find Blog content After posting')

        # confirm content is correct:
        self.assertEqual(blog_title.text, 'Generic Post of A Edited')
        self.assertEqual(blog_author.text, 'thinga')
        self.assertEqual(blog_content.text, 'Generic general first post of A Edited')


if __name__ == '__main__':
    unittest.main()
