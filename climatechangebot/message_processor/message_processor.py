"""
    Message processor - the heart of our robot

    Parse messages from Facebook:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference



"""

import random

from config import Config
from response_dicts import *
# from bot_interface.bot_interface import NotificationType, RecipientMethod


class FacebookMessage(object):
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


class MessageProcessor(object):
    def __init__(self, bot, wit):
        self.BOT = bot
        self.WIT = wit

    def parse_messages(self, messages):
        """
            Parses messages from Facebook as they come in, and chooses which actions
            to execute depending on the message type


            :rtype: NOT SURE WHAT THIS SHOULD RETURN YET
        """

        if Config.DEVELOPMENT:
            print(messages)

        for entry in messages['entry']:
            for m in entry['messaging']:
                recipient_id = m['sender']['id']

                if m.get('message'):
                    """
                        Either an attachment or a text message will be parsed here
                            and sent to the Wit Processor, which will send a response
                            to the user
                    """

                    message = FacebookMessage(m)

                    # We are assuming that a message has either a text payload or an image payload
                    #   but not both
                    if message.message_text:
                        #call witprocessor here
                        print(message.message_text)


                    if message.message_attachments:
                        # send a random gif
                        gif_attachment_url = self.get_rand_gif()
                        response = self.BOT.send_image_payload_message(recipient_id,
                                                                       image_url=gif_attachment_url)

                    # response = self.BOT.send_text_message(recipient_id, message,
                                    # RecipientMethod.ID.value, NotificationType.REGULAR.value)

                    # process text message
                    # self.parse_text_message(message, recipient_id)

                    # return response.status_code

                elif m.get('postback'):
                    """
                        Someone clicks on a postback message we sent
                    """
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
                    if Config.DEVELOPMENT:
                        print('got optin %s' % optin_ref)
                elif m.get('account_linking'):
                    """
                        For letting users login to our app accounts through FB messenger
                    """
                    account_linking_status = m['account_linking']['status']
                    print('got account_linking status: %s' % account_linking_status)
                elif m.get('delivery'):
                    """
                        FB is letting us know that a message was delivered
                        You can subscribe to this callback by selecting the message_deliveries field
                        when setting up your webhook.
                    """
                    delivery = m['delivery']
                    mid_array = delivery['mids']
                    if Config.DEVELOPMENT:
                        print('got message delivery notification for %s' % str(mid_array))
                elif m.get('read'):
                    """
                        Notifies us that a user read a message
                    """
                    read = m['read']
                    read_watermark = read['watermark']
                    read_seq = read['seq']
                    if Config.DEVELOPMENT:
                        print('got message read notificaiton watermark: %s seq: %s' % (read_watermark, read_seq))
                else:
                    pass

    def get_rand_int(self, max_int):
        return random.randint(0, max_int)

    def get_rand_gif(self, gif_type="TEMPERATURE"):
        """
            Gets a random gif given a gif type from the gif_dicts

        """
        gif_links = gif_dict[gif_type]
        max_int = len(gif_links) - 1
        return gif_links[self.get_rand_int(max_int)]
