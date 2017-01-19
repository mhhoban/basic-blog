"""
module for registration functions
"""
from db_schema import User
from google.appengine.ext import ndb
from hasher import hash_password


def registration(username, password, penname):
    """
    creates a new registration entry in the db
    :param username:
    :param password:
    :param penname:
    :return:
    """

    # hash password for security
    password = hash_password(password)

    new_user = User(email=username, password=password, penname=penname)
    new_user.key = ndb.Key('User', new_user.email)
    new_user.put()
