from google.appengine.ext import ndb

from db_schema import Post


def get_all_posts():

    # import pdb
    # pdb.set_trace()

    all_posts = Post.query().fetch()

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

    import pdb
    pdb.set_trace()

    new_post = Post(author=blog_post['author'],
                    title=blog_post['title'],
                    content=blog_post['content'])

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


