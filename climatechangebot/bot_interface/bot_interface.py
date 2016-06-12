"""
    Interface to communicate with Facebook Messenger
    https://developers.facebook.com/docs/messenger-platform/send-api-reference
"""

import json
import requests

from enum import Enum


class NotificationType(Enum):
    REGULAR = "REGULAR"
    SILENT_PUSH = "SILENT_PUSH"
    NO_PUSH = "NO_PUSH"


class RecipientMethod(Enum):
    ID = "id"
    PHONE_NUMBER = "phone_number"


class BotInterface(object):
    def __init__(self, messaging_url):
        self.URL = messaging_url

    def send_text_message(self, recipient_info, message,
                          recipient_method="id", notification_type="REGULAR"):

        recipient_json = {recipient_method: recipient_info}

        message = {
            'recipient': recipient_json,
            'message': {
                'text': message
            },
            'notification_type': notification_type
        }

        return self._send(message)

    def _send(self, message_json):
        response = requests.post(self.URL, json=message_json,
                                 headers={"Content-Type": "application/json"})

        return response
