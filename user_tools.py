"""
methods to help with user related operations
"""

from google.appengine.ext import ndb
from hasher import hash_password


def fetch_user(user_id):

    user_key = ndb.Key('User', user_id)

    user = user_key.get()

    return user


def login_exists(email):
    user.key = ndb.Key('User', email)

    if user.key.get():
        return True

    else:
        return False


def fetch_penname(user_id):

    user = fetch_user(user_id)

    return user.penname


def check_password(user_id, password):

    user = fetch_user(user_id)

    password = hash_password(password)

    if password == user.password:
        return True

    else:
        return False
