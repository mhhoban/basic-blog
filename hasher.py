"""
Methods for password and cookie hashing
"""

import hmac
import json


def get_salts():
    salt_file = open('salts.data', 'r')
    salts = salt_file.read()
    salt_file.close()
    salts = json.loads(salts)

    return salts


def encode_cookie(user):
    """
    hash the username for cookie encoding
    :param user:
    :return:
    """

    salts = get_salts()

    hash = hmac.new(str(salts['cookies']), user).hexdigest()
    hashed_cookie = user + '-' + hash

    return hashed_cookie


def hash_password(password):
    """
    hashes the plaintext password and returns the hash

    :param password:
    :return:
    """

    salts = get_salts()

    pass_hash = hmac.new(str(salts['passwords']), password).hexdigest()

    return pass_hash


def verify_cookie(hashed_cookie):
    """
    verify the hash matches the data.
    :param hashed_cookie: String List, [0] is user_name, [1] is hash
    :return:
    """

    salts = get_salts()

    hash = hmac.new(str(salts['cookies']), hashed_cookie[0]).hexdigest()

    if hash == hashed_cookie[1]:
        return True

    else:
        return False
