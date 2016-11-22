import hmac


def encode_cookie():

    cookie_hash = hmac.new("arbitrary-secret", "test-hash").hexdigest()

    return cookie_hash


def verify_cookie(hashed_cookie):

    hash = hmac.new('arbitrary-secret', hashed_cookie[0]).hexdigest()

    import pdb
    pdb.set_trace()

    if hash == hashed_cookie[1]:
        return True

    else:
        return False


