"""
    User model object for mongo
"""


class User(object):
    def __init__(self):
        self.user_vars_template = {
            "rive_name": None,
            "rive_age": None,
            "profile_pic": None,
            "first_name": None,
            "last_name": None,
            "locale": None,
            "gender": None,
            "timezone": None,
            "created_timestamp": None
        }

        self.user_dict = {
            "recipient_id": "",
            "user_vars": self.user_vars_template
        }

        self.FB_VARS = ['profile_pic', 'first_name', 'last_name', 'locale', 'gender', 'timezone']

    def set_user_dict(self, recipient_id, fb_user_profile_info, timestamp):
        self.user_dict['recipient_id'] = recipient_id

        for fb in self.FB_VARS:
            if fb_user_profile_info.get(fb):
                self.user_dict['user_vars'][fb] = fb_user_profile_info[fb]

        self.user_dict['user_vars']['created_timestamp'] = timestamp

    def update_user_vars(self, new_user_vars):
        if not self.user_dict.get('user_vars'):
            self.user_dict['user_vars'] = self.user_vars_template
        else:
            # If not passed to Rive, these keys won't be in the new_user_vars response
            #   from Rive
            self.user_dict['user_vars']['rive_name'] = new_user_vars['rive_name']
            self.user_dict['user_vars']['rive_age'] = new_user_vars['rive_age']

        # These keys will always be in the new_user_vars, the above keys may not be if they
        #   were not properly passed in to set_uservar
        self.user_dict['user_vars']['topic'] = new_user_vars['topic']
        self.user_dict['user_vars']['__history__'] = new_user_vars['__history__']
        self.user_dict['user_vars']['__lastmatch__'] = new_user_vars['__lastmatch__']
