"""
methods for dealing with blog posts
"""
from cgi import escape
from datetime import datetime
from db_schema import Post
from google.appengine.ext import ndb

import hmac
import json


def add_comment(blog_id, commenter, comment_content):
    """
    add a comment to a blog post
    :param blog_id:
    :param commenter:
    :param comment_content:
    :return:
    """
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)
    timestamp = get_timestamp()
    comment = {}
    comment['commenter'] = commenter
    comment['content'] = escape(comment_content, quote=True)
    comment['timestamp'] = timestamp
    comment['comment_id'] = gen_comment_id(commenter, comment_content,
                                           target_post.title, timestamp)
    comments.append(comment)
    comments = json.dumps(comments)
    target_post.comments = comments

    if target_post.put():
        return True

    else:
        return False


def add_post_like(blog_id, liker):
    """
    add a like to a blog post
    :param blog_id:
    :param liker:
    :return:
    """
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


def blog_data_parser(blog_post_data):
    """
    breaks down data about a blog post from the POST request for processing
    :param blog_post_data:
    :return: dict
    """

    try:
        author = blog_post_data['author']
    except KeyError:
        author = ''

    try:
        title = escape(blog_post_data['title'], quote=True)
    except KeyError:
        title = ''

    try:
        content = escape(blog_post_data['content'], quote=True)
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


def delete_comment(blog_id, comment_id):
    """
    remove a comment from a blog post
    :param blog_id:
    :param comment_id:
    :return:
    """
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


def delete_post(blog_id):
    """
    Deletes a blog post

    :param blog_id: long id of blog post to be deleted
    :return: True/False for success of deletion
    """
    target_post_key = ndb.Key('Post', blog_id)

    target_post_key.delete()

    if target_post_key.get() is None:
        return True

    else:
        return False


def edit_comment(blog_id, comment_id, comment_content):
    """
    edit the content of a comment on a blog post
    :param blog_id:
    :param comment_id:
    :param comment_content:
    :return:
    """
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    # iterate through comments to find index of target comment,
    # then replace its content

    for comment in comments:
        if comment['comment_id'] == comment_id:
            comment['content'] = escape(comment_content, quote=True)
            break

    comments = json.dumps(comments)
    target_post.comments = comments

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


def get_all_posts():
    """
    returns all posts users have stored thus far
    :return: all_posts
    """

    all_posts = Post.query().fetch()

    return all_posts


def get_comment_author(blog_id, comment_id):
    """
    returns the author of a specific comment
    :param blog_id:
    :param comment_id:
    :return:
    """
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
    """
    get all the data for a specific comment
    :param blog_id:
    :param comment_id:
    :return:
    """

    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    requested_comment = False

    for comment in comments:
        if comment['comment_id'] == comment_id:
            requested_comment = comment

    return requested_comment


def get_post_author(blog_id):
    """
    returns the author of the blog whose id is provided
    :param blog_id:
    :return: target_post.author
    """

    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    return target_post.author


def get_post_comments(blog_id):
    """
    returns list of comments left on specified blog post
    :param blog_id:
    :return:
    """
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_comments = target_post.comments
    comments = json.loads(json_comments)

    return comments


def get_post_comment_total(blog_id):
    """
    returns integer total of comments left on blog post
    :param blog_id:
    :return:
    """

    comments = get_post_comments(blog_id)
    return len(comments)


def get_post_data(blog_id):
    """
    gets all raw data for a blog post whose id is provided
    :param blog_id:
    :return:
    """
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    return target_post


def get_post_likes(blog_id):
    """
    return a list of all the users who have liked the post whose id is provided
    :param blog_id:
    :return:
    """
    target_post_key = ndb.Key('Post', blog_id)
    target_post = target_post_key.get()

    json_likes = target_post.likes
    likes = json.loads(json_likes)

    return likes


def get_timestamp():
    """
    returns a formatted string for a timestamp when called
    :return:
    """
    raw_time = datetime.now()
    string_time = raw_time.strftime('%H:%M %m/%d/%Y')

    return string_time


def store_post(blog_post_data):
    """
    Stores new blog post in db
    :param blog_post_data:
    :return: True/False
    """

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
    """
    updates the data in a blog post
    :param blog_post_data:
    :return: True/False
    """

    target_post_key = ndb.Key('Post', long(blog_post_data['blog_id']))
    target_post = target_post_key.get()

    target_post.title = escape(blog_post_data['title'], quote=True)
    target_post.content = escape(blog_post_data['content'])

    if target_post.put():

        return True

    else:

        return False
