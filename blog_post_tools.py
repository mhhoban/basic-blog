from google.appengine.ext import ndb
import json
import hmac
from datetime import datetime
from db_schema import Post


def get_all_posts():

    all_posts = Post.query().fetch()

    return all_posts


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

    post_likes = {}
    post_likes = json.dumps(post_likes)

    post_comments = []
    post_comments = json.dumps(post_comments)

    new_post = Post(author=blog_post['author'],
                    title=blog_post['title'],
                    content=blog_post['content'],
                    likes=post_likes,
                    comments=post_comments)

    new_post.put()

    if new_post.put():
        return True
    else:
        return False


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


def get_post_comments(blog_id):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    return comments


def get_post_comment_total(blog_id):

    comments = get_post_comments(blog_id)
    return len(comments)


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


def gen_comment_id(commenter, comment, post_title, timestamp):

    """
    Generate ID for comment.
    :param commenter: string pen name of user leaving comment
    :param comment: string content of comment
    :param post_title: string title of comment
    :param timestamp: datetime timestamp
    :return:
    """

    hash_seed = commenter + comment + post_title + timestamp
    hash_seed = str(hash_seed)

    comment_id = hmac.new(hash_seed).hexdigest()

    return comment_id


def add_comment(blog_id, commenter, comment_content):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)
    timestamp = get_timestamp()
    comment = {}
    comment['commenter'] = commenter
    comment['content'] = comment_content
    comment['timestamp'] = timestamp
    comment['comment_id'] = gen_comment_id(commenter, comment_content, target_post.title, timestamp)
    comments.append(comment)
    comments = json.dumps(comments)
    target_post.comments = comments

    if target_post.put():
        return True

    else:
        return False


def get_comment_author(blog_id, comment_id):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    post_author = False

    for comment in comments:
        if comment['comment_id'] == comment_id:
            post_author = comment['commenter']

    return post_author


def get_comment_data(blog_id, comment_id):

    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    requested_comment = False

    for comment in comments:
        if comment['comment_id'] == comment_id:
            requested_comment = comment

    return requested_comment


def delete_comment(blog_id, comment_id):
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    # iterate through comments to find index of target comment,
    # then pop comment from list

    iter = 0
    for comment in comments:
        if comment['comment_id'] == comment_id:
            comments.pop(iter)
            break
        iter += 1

    comments = json.dumps(comments)
    target_post.comments = comments

    if target_post.put():
        return True

    else:
        return False


def get_timestamp():
    raw_time = datetime.now()
    string_time = raw_time.strftime('%H:%M %m/%d/%Y')

    return string_time
