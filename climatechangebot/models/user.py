"""
    User model object for mongo
"""


class User(object):
    def __init__(self):
        self.user_dict = {
            "recipient_id": "",
            "user_vars": {
                "name": "",
                "age": 0,
                "profile_pic": None,
                "first_name": None,
                "last_name": None,
                "locale": None,
                "gender": None,
                "timezone": None,
                "created_timestamp": None
            }
        }

        self.FB_VARS = ['profile_pic', 'first_name', 'last_name', 'locale', 'gender', 'timezone']

    def set_user_dict(self, recipient_id, fb_user_profile_info):
        self.user_dict['recipient_id'] = recipient_id

        for fb in self.FB_VARS:
            if fb_user_profile_info.get(fb):
                self.user_dict['user_vars'][fb] = fb_user_profile_info[fb]

    def update_user_vars(self, new_user_vars):
        print(new_user_vars)
        self.user_dict['user_vars']['age'] = new_user_vars['age']
        self.user_dict['user_vars']['topic'] = new_user_vars['topic']
        self.user_dict['user_vars']['__history__'] = new_user_vars['__history__']
        self.user_dict['user_vars']['__lastmatch__'] = new_user_vars['__lastmatch__']
