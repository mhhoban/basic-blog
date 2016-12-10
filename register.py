"""
module for registration functions
"""
from db_schema import User
from google.appengine.ext import ndb


def registration(username, password, penname):

    new_user = User(email=username, password=password, penname=penname)
    new_user.key = ndb.Key('User', new_user.email)
    new_user.put()


def delete_registration(username):
    key = ndb.Key('User', username)
    key.delete()