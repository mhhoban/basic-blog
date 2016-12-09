#from google.appengine.ext import ndb

from db_schema import Posts


def get_all_posts():

    # import pdb
    # pdb.set_trace()

    all_posts = Posts.query()

    if all_posts.count() > 0:
        return True

    else:
        return False
