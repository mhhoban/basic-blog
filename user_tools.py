from google.appengine.ext import ndb


def fetch_user(user_id):

    user_key = ndb.Key('Users', user_id)

    user = user_key.get()

    return user


def login_exists(email):
    user.key = ndb.Key('Users', email)

    if (user.key.get()):
        return True

    else:
        return False


def fetch_penname(user_id):

    # user_key = ndb.Key('Users', email)
    #
    # user = user_key.get()

    user = fetch_user(user_id)

    return user.penname


def check_password(user_id, password):

    user = fetch_user(user_id)

    if password == user.password:
        return True

    else:
        return False

