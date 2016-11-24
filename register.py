"""
module for registration functoins
"""
from db_schema import Users
from google.appengine.ext import ndb


def registration(username, password):

    new_user = Users(email=username, password=password)
    new_user.key = ndb.Key('Users', new_user.email)
    new_user.put()


