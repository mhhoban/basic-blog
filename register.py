"""
module for registration functions
"""
from db_schema import Users
from google.appengine.ext import ndb


def registration(username, password, penname):

    new_user = Users(email=username, password=password, penname=penname)
    new_user.key = ndb.Key('Users', new_user.email)
    new_user.put()


def delete_registration(username):
    key = ndb.Key('Users', username)
    key.delete()