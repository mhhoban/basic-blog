from cookie_hasher import verify_cookie
from user_tools import fetch_penname


def auth_user(self):

    try:
        user_hash = self.request.cookies.get('user-id', 'None')

    except AttributeError:
        user_hash = self.request.cookies.post('user-id', 'None')

    # import pdb
    # pdb.set_trace()

    if user_hash != 'None':
        user_hash = user_hash.split('-')

        if verify_cookie(user_hash):
            user_id = user_hash[0]
            penname = fetch_penname(user_id)
            return {'authorized': True, 'user_id': user_id, 'penname': penname}

        else:
            return {'authorized': False}
    else:
        return {'authorized': False}