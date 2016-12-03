from google.appengine.ext import ndb
from db_schema import Users


def login_fields_complete(post_data):

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

    user_key = ndb.Key('Users', user_id)

    user = user_key.get()

    if user:
        return True

    else:
        return False
