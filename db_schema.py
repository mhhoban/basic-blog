"""
(Kind) Users:

    (Entity): User

        (Field): Name
        (Field): email
        (Field): password
        (ID): email


(Kind) Posts:

    (Entity): Post

        (Field): Title
        (Field): Content
        (Parent): User


"""
from google.appengine.ext import ndb


class Users(ndb.Model):

    email = ndb.StringProperty()
    password = ndb.StringProperty()
    penname = ndb.StringProperty()

class Posts(ndb.Model):

    author = ndb.StringProperty()
    title = ndb.StringProperty()
    content = ndb.TextProperty()
    publish_date = ndb.DateTimeProperty()
    likes = ndb.IntegerProperty()







