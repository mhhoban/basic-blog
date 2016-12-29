from google.appengine.ext import ndb
import json
from db_schema import Post


def get_all_posts():

    all_posts = Post.query().fetch()

    # import pdb
    # pdb.set_trace()

    return all_posts

    # posts = []

    # if all_posts.count() > 0:
    #     return posts
    #
    # else:
    #     # for post in all_posts:
    #     return False


def blog_data_parser(blog_post_data):

    try:
        author = blog_post_data['author']
    except KeyError:
        author = ''

    try:
        title = blog_post_data['title']
    except KeyError:
        title = ''

    try:
        content = blog_post_data['content']
    except KeyError:
        content = ''

    blog_post = {}

    if len(author) > 0 and len(title) > 0 and len(content) > 0:
        blog_post['author'] = author
        blog_post['title'] = title
        blog_post['content'] = content
        blog_post['valid'] = True

    else:
        blog_post['valid'] = False

    return blog_post


def store_post(blog_post_data):

    blog_post = blog_data_parser(blog_post_data)

    # new_key = db.Key.from_path('Post', new_key_id[0])
    #
    # import pdb
    # pdb.set_trace()

    post_likes = {}
    post_likes = json.dumps(post_likes)

    new_post = Post(author=blog_post['author'],
                    title=blog_post['title'],
                    content=blog_post['content'],
                    likes=post_likes)

    new_post.put()

    # import pdb
    # pdb.set_trace()

    if new_post.put():
         return True
    else:
         return False

    # new_user = User(email=username, password=password, penname=penname)
    # new_user.key = ndb.Key('User', new_user.email)
    # new_user.put()

    # import pdb
    # pdb.set_trace()
    #
    # query = Post.query()


def update_post(blog_post_data):

    target_post_key = ndb.Key('Post', long(blog_post_data['blog_id']))
    target_post = target_post_key.get()

    target_post.title = blog_post_data['title']
    target_post.content = blog_post_data['content']

    if target_post.put():

        return True

    else:

        return False


def get_post_author(blog_id):

    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    return target_post.author


def get_post_data(blog_id):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    return target_post


def get_post_likes(blog_id):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_likes = target_post.likes
    likes = json.loads(json_likes)

    return likes


def add_post_like(blog_id, liker):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_likes = target_post.likes
    likes = json.loads(json_likes)
    likes[liker] = True
    json_likes = json.dumps(likes)
    target_post.likes = json_likes

    if target_post.put():

        return True

    else:

        return False
