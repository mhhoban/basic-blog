"""
methods to help with user related operations
"""

from google.appengine.ext import ndb
from hasher import hash_password


def fetch_user(user_id):
    """
    Fetches a user's data from the db based on their key id
    :param user_id:
    :return:
    """

    user_key = ndb.Key('User', user_id)

    user = user_key.get()

    return user


def login_exists(email):
    """
    Checks whether a user exists.
    :param email:
    :return:
    """
    user.key = ndb.Key('User', email)

    if user.key.get():
        return True

    else:
        return False


def fetch_penname(user_id):
    """
    fetches a user's pen name
    :param user_id:
    :return:
    """

    user = fetch_user(user_id)

    return user.penname


def check_password(user_id, password):
    """
    checks whether the user's password is correct
    :param user_id:
    :param password:
    :return:
    """

    user = fetch_user(user_id)

    password = hash_password(password)

    if password == user.password:
        return True

    else:
        return False
