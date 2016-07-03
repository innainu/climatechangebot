"""
    Message processor - the heart of our robot

    Parse messages from Facebook:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference



"""

# from bot_interface.bot_interface import NotificationType, RecipientMethod
from image_dicts import *

import random


class MessageProcessor(object):
    def __init__(self, bot):
        self.BOT = bot

    def parse_messages(self, messages):
        """
            Parses messages from Facebook as they come in


            :rtype: not sure what this should return yet
        """

        print(messages)

        for entry in messages['entry']:
            for m in entry['messaging']:
                recipient_id = m['sender']['id']

                if m.get('message'):

                    message = Message(m)

                    if message.message_text:
                        print(message.message_text)

                    if message.message_attachments:
                        # send a random gif
                        gif_links = gif_dict['TEMPERATURE']
                        max_int = len(gif_links) - 1
                        gif_attachment_url = gif_links[self.get_rand_int(max_int)]

                        response = self.BOT.send_image_payload_message(recipient_id,
                                                                       image_url=gif_attachment_url)

                    # response = self.BOT.send_text_message(recipient_id, message,
                                    # RecipientMethod.ID.value, NotificationType.REGULAR.value)

                    # process text message
                    # self.parse_text_message(message, recipient_id)

                    # return response.status_code

                elif m.get('postback'):
                    # someone clicks on a postback message we sent
                    postback_paylod = m['postback']['payload']
                    print('got postback %s' % postback_paylod)
                elif m.get('optin'):
                    """
                        This callback will occur when the Send-to-Messenger plugin has been tapped.
                            The optin.ref parameter is set by the data-ref field on the
                            "Send to Messenger" plugin. This field can be used by the developer
                            to associate a click event on the plugin with a callback. You can
                            subscribe to this callback by selecting the messaging_optins field
                            when setting up your webhook.
                    """
                    optin_ref = m['optin']['ref']
                    print('got optin %s' % optin_ref)
                elif m.get('account_linking'):
                    # for letting users login to our app accounts through FB messenger
                    account_linking_status = m['account_linking']['status']
                    print('got account_linking status: %s' % account_linking_status)
                elif m.get('delivery'):
                    # FB is letting us know that a message was delivered
                    # You can subscribe to this callback by selecting the message_deliveries field
                    #   when setting up your webhook.
                    delivery = m['delivery']
                    mid_array = delivery['mids']
                    print('got message delivery notification for %s' % str(mid_array))
                elif m.get('read'):
                    # Notifies us that a user read a message
                    read = m['read']
                    read_watermark = read['watermark']
                    read_seq = read['seq']
                    print('got message read notificaiton watermark: %s seq: %s' % (read_watermark, read_seq))
                else:
                    pass

    def get_rand_int(self, max_int):
        return random.randint(0, max_int)


class Message(object):
    def __init__(self, m):
        self.timestamp = m['timestamp']
        message = m['message']

        self.message_id = message['mid']
        self.message_seq_num = message['seq']

        if message.get('text'):
            self.message_text = message['text']
        else:
            self.message_text = None

        if message.get('attachments'):
            self.message_attachments = message['attachments']
        else:
            self.message_attachments = None
