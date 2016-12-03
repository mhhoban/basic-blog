from google.appengine.ext import ndb


def login_exists(email):
    user.key = ndb.Key('Users', email)

    if (user.key.get()):
        return True

    else:
        return False


def fetch_penname(email):

    user_key = ndb.Key('Users', email)

    user = user_key.get()

    return user.penname


