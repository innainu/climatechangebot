"""
    Creates the welcome message for our bot by sending a request to Facebook.

    Edit the message_json and run either:
        $ python welcome_message.py --action create
    OR
        $ python welcome_message.py --action delete
"""

import sys
import os.path
import argparse
import requests
import ConfigParser

# Append parent directory to python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

from config import Config

# Get some configs
config = ConfigParser.ConfigParser()
config.read("../local_test_config.cfg")

FB_MESSAGING_URL = (
    "https://graph.facebook.com"
    "/v{0}/852964301474501/thread_settings?access_token={1}"
).format(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))


def create_welcome_message():

    message_json = {
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": [{
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Welcome to the climatechangebot thread!",
                                "item_url": "https://www.facebook.com/climatechangebot/",
                                "image_url": "https://scontent-lga3-1.xx.fbcdn.net/t31.0-8/13422214_852984424805822_3203580027459777074_o.jpg",
                                "subtitle": "Stay informed about climate change so that we can make a difference!",
                                # "buttons":[
                                #   {
                                #     "type": "web_url",
                                #     "title": "View Website",
                                #     "url": "https://www.petersbowlerhats.com"
                                #   },
                                #   {
                                #     "type": "postback",
                                #     "title": "Start Chatting",
                                #     "payload": "DEVELOPER_DEFINED_PAYLOAD"
                                #   }
                                # ]
                            }
                        ]
                    }
                }
            }
        }]
    }

    response = requests.post(FB_MESSAGING_URL,
        json=message_json,
        headers={"Content-Type": "application/json"})

    print(response.content)
    if response.status_code == 200:
        print('Success CREATE!!')
    else:
        raise Exception('Message update failed!')


def delete_welcome_message():
    message_json = {
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": []
    }

    response = requests.post(FB_MESSAGING_URL,
        json=message_json,
        headers={"Content-Type": "application/json"})

    print(response.content)
    if response.status_code == 200:
        print('Success DELETE!!')
    else:
        raise Exception('Message update failed!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Change welcome message.')
    parser.add_argument('--action', type=str,
                        help='should I create or delete welcome message?')

    args = parser.parse_args()
    if args.action == "delete":
        delete_welcome_message()
    else:
        create_welcome_message()
