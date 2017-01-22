#BasicBlog: A Basic Multi-User Blog

Basic blog is a bare bones multi-user blog system that allows authenticated users to
write blog posts, like the blog posts of others, and comment on blog posts.

##Requirements:

BasicBlog is designed for use with Google App Engine, and running the project in a
development environment requires having the GAE SDK for python installed locally
(https://cloud.google.com/appengine/docs/python/download).

The project is also designed to work with Python 2.7 and the setup.py script uses
PIP. While running the setup script in a virtual environment is not required, it is
highly recommended.


##Setup:

Run the setup scrip with: `python setup.py`

The script will prompt you to pick two strings to use as salts for password and cookie
hashing, and will then use PIP to install the project's necessary packages.


##Unit and Functional Tests:

BasicBlog comes with unit tests and functional tests.

###Unit Tests:

You can run the unit tests from the project's base directory with

```
python test_runner.py -unit
```

###Functional Tests:

The functional tests that come with BasicBlog use selenium and are written for
the selenium Chrome WebDriver. The project comes with the driver for MacOS,
but if you want to run the functional tests on other OSes you can download the
corresponding Chrome Webdriver,
(https://sites.google.com/a/chromium.org/chromedriver/downloads) and replace the
bundled "chromedriver" file with the one you downloaded then rename the downloaded file
"chromedriver" instead. Make sure you only have one "chromedriver" file in the project's
base directory.

When you have the appropriate WebDriver, you can run the functional tests with:
```
python test_runner.py -functional
```

Note that selenium can be temperamental at times and you might have to run the tests a second
time before it begins behaving properly.


##License:

Project is freely open source under the terms of the
[MIT License](http://choosealicense.com/licenses/mit/)

