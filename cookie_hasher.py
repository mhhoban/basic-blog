import hmac


def encode_cookie(user):
    """
    hash the username for cookie encoding
    :param user:
    :return:
    """

    hash = hmac.new("arbitrary-secret", user).hexdigest()
    hashed_cookie = user + ',' + hash

    return hashed_cookie


def verify_cookie(hashed_cookie):
    """
    verify the hash matches the data.
    :param hashed_cookie: String List, [0] is user_name, [1] is hash
    :return:
    """

    hash = hmac.new('arbitrary-secret', hashed_cookie[0]).hexdigest()

    if hash == hashed_cookie[1]:
        return True

    else:
        return False


