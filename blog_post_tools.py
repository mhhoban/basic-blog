#from google.appengine.ext import ndb

from db_schema import Post


def get_all_posts():

    # import pdb
    # pdb.set_trace()

    all_posts = Post.query()

    if all_posts.count() > 0:
        return True

    else:
        return False
