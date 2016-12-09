"""
(Kind) User:

    (Entity): a user

        (Field): Name
        (Field): email
        (Field): password
        (ID): email


(Kind) Post:

    (Entity): a post

        (Field): Title
        (Field): Content
        (Parent): User


"""
from google.appengine.ext import ndb


class User(ndb.Model):

    email = ndb.StringProperty()
    password = ndb.StringProperty()
    penname = ndb.StringProperty()


class Post(ndb.Model):

    author = ndb.StringProperty()
    title = ndb.StringProperty()
    content = ndb.TextProperty()
    publish_date = ndb.DateTimeProperty()
    likes = ndb.IntegerProperty()







