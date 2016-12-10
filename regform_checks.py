"""
functions to validate registraiton data
"""

import re
from google.appengine.ext import ndb
from db_schema import User


def all_fields_complete(post_data):
    """
    check all fields are present
    :param post_data:
    :return:
    """

    reg_fields = get_reg_fields(post_data)

    user_email = reg_fields[0]
    password = reg_fields[1]
    password_rep = reg_fields[2]
    penname = reg_fields[3]

    if len(user_email) > 0 and len(password) > 0 and len(password_rep) > 0 and len(penname) > 0:
        return {'fields_present': True, 'email': user_email, 'password': password,
                'password_rep': password_rep, 'penname': penname}

    else:
        return {'fields_present': False, 'email': user_email, 'password': password,
                'password_rep': password_rep, 'penname': penname}


def get_reg_fields(post_data):
    """
    extract all reg_fields.
    :param post_data:
    :return:
    """

    # try/except clauses to catch missing input

    try:
        user_email = post_data['email']
    except KeyError:
        user_email = ''

    try:
        penname = post_data['penname']
    except KeyError:
        penname = ''

    try:
        password = post_data['password']
    except KeyError:
        password = ''

    try:
        password_rep = post_data['password_rep']
    except KeyError:
        password_rep = ''

    return [user_email, password, password_rep, penname]


def valid_email_check(email):
    re_pattern = '[a-zA-Z._]+[@][a-zA-Z]+[.][a-zA-z]+'
    valid = re.match(re_pattern, email)
    return valid


def duplicate_email_check(email):
    """
    return True if not duplicate, False if duplicate
    :param email:
    :return:
    """

    query = User.query(User.email == email)

    if len(query.fetch()) > 0:
        return False

    else:
        return True


def nom_de_plume_available(penname):
    """
    checks that nom_de_plume is still available
    :param penname:
    :return: True if available, false if not
    """

    query = User.query(User.penname == penname)

    if len(query.fetch()) > 0:
        return False

    else:
        return True


def passwords_match_check(password, password_rep):
    if password == password_rep:
        return True

    else:
        return False
