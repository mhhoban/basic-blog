"""
Methods for user login
"""
from google.appengine.ext import ndb


def login_fields_complete(post_data):
    """
    validates that both login fields were filled in
    :param post_data:
    :return:
    """

    try:
        user_id = post_data['user_id']
    except KeyError:
        user_id = False

    try:
        password = post_data['password']
    except KeyError:
        password = False

    if user_id and password:
        return {'complete': True, 'user_id': user_id, 'password': password}

    else:
        return {'complete': False}


def valid_user_id_check(user_id):
    """
    checks that user exists
    :param user_id:
    :return:
    """

    user_key = ndb.Key('User', user_id)

    user = user_key.get()

    if user:
        return True

    else:
        return False
