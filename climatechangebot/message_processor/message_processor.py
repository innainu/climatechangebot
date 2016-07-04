"""
    Message processor - the heart of our robot

    Parse messages from Facebook:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference


    TO DO:
        - Cannot compute: should have a helper call back button and "View trending"
        - Make bot conversational using api.ai
        - Build out Wit.ai search functionaility

"""

import random

from wit import Wit
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


class WitParsedMessage():
    def __init__(self, text, entities, intent):
        self.text = text
        self.entities = entities
        self.intent = intent


class WitParser(object):
    """
        Gets entities from wit.ai

        - each entity gets a confidence value from 0 to 1.
            "1 is extremely confident. Lower than 0.5 is considered very low confidence."

        - can add intents using api:
        https://wit.ai/docs/http/20160330#get-intent-via-text-link

    """

    def __init__(self, key, bot, nyt_api):
        #define actions
        self.actions = {}
        self.wit_client = Wit(access_token=key, actions=self.actions)
        self.BOT = bot
        self.NYT_API = nyt_api
        self.SEARCH_QUERY_CONFIDENCE_THRESH = 0.5

    def wit_api_call(self, text):
        wit_response = self.wit_client.message(text)
        wit_parsed_message = self.parse_wit_response(wit_response, text)
        return wit_parsed_message

    def parse_wit_response(self, wit_return_dict, text):
        """
            Takes a Wit response dict and converts into a WitParsedMessage object
        """
        entities = []
        intent = None
        wit_entities = wit_return_dict['entities']

        if 'intent' in wit_entities:
            intent = (wit_entities['intent'][0]['value'], wit_entities['intent'][0]['confidence'])

        if 'search_query' in wit_entities:
            for ent in wit_entities['search_query']:
                entities.append((ent['value'], ent['confidence']))

        wit_parsed_message = WitParsedMessage(text, entities, intent)
        return wit_parsed_message

    def wit_take_action(self, wit_parsed_message, recipient_id, num=1):
        """
            Sends messages to the user on behalf of the Wit Parser
        """
        if wit_parsed_message.intent and wit_parsed_message.intent[0] == 'search_article' \
                and wit_parsed_message.intent[1] > self.SEARCH_QUERY_CONFIDENCE_THRESH \
                and len(wit_parsed_message.entities) > 0:
            #take entitiy with highest confidence
            ent = sorted(wit_parsed_message.entities, key=lambda x: x[1], reverse=True)[0]
            nyt_response = self.NYT_API.return_article_list(ent[0], num=num)

            template_elements = []
            for nyt in nyt_response:

                if nyt.get("image_url"):
                    nyt_image_url = nyt["image_url"]
                else:
                    nyt_image_url = None

                template_elements.append(
                    self.BOT.create_generic_template_element(
                        element_title=nyt["title"], element_item_url=nyt["web_url"],
                        element_image_url=nyt_image_url, element_subtitle=nyt["abstract"]
                    )
                )

            response = self.BOT.send_generic_payload_message(recipient_id, elements=template_elements)

        else:
            response = self.BOT.send_text_message(recipient_id, "Cannot compute.")

        return response

    def send_cannot_compute_helper_callback(self):
        pass


class MessageProcessor(object):
    """
        Processes incoming messages from Facebook and directs functionaility
            to WitParser or other parsing objects that send responses back to the user
    """

    def __init__(self, bot, wit, config):
        self.BOT = bot
        self.WIT = wit
        self.CONFIG = config

    def parse_messages(self, messages):
        """
            Parses messages from Facebook as they come in, and chooses which actions
            to execute depending on the message type


            :rtype: response from requests.post() method
        """
        print('debug is ' + str(self.CONFIG['DEBUG']))
        if self.CONFIG['DEBUG']:
            print(messages)

        for entry in messages['entry']:
            for m in entry['messaging']:
                response = None
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
                        wit_parsed_message = self.WIT.wit_api_call(message.message_text)
                        response = self.WIT.wit_take_action(wit_parsed_message, recipient_id, 3)

                    elif message.message_attachments:
                        # send a random gif
                        gif_attachment_url = self.get_rand_gif()
                        response = self.BOT.send_image_payload_message(recipient_id,
                                                                       image_url=gif_attachment_url)

                elif m.get('postback'):
                    """
                        Someone clicks on a postback message we sent
                    """

                    postback_paylod = m['postback']['payload']
                    if self.CONFIG['DEBUG']:
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
                    if self.CONFIG['DEBUG']:
                        print('got optin %s' % optin_ref)
                elif m.get('account_linking'):
                    """
                        For letting users login to our app accounts through FB messenger
                    """

                    account_linking_status = m['account_linking']['status']
                    if self.CONFIG['DEBUG']:
                        print('got account_linking status: %s' % account_linking_status)
                elif m.get('delivery'):
                    """
                        FB is letting us know that a message was delivered
                        You can subscribe to this callback by selecting the message_deliveries field
                        when setting up your webhook.
                    """

                    delivery = m['delivery']
                    mid_array = delivery['mids']
                    if self.CONFIG['DEBUG']:
                        print('got message delivery notification for %s' % str(mid_array))
                elif m.get('read'):
                    """
                        Notifies us that a user read a message
                    """

                    read = m['read']
                    read_watermark = read['watermark']
                    read_seq = read['seq']
                    if self.CONFIG['DEBUG']:
                        print('got message read notificaiton watermark: %s seq: %s' % (read_watermark, read_seq))
                else:
                    pass

            if response:
                return response

    def get_rand_int(self, max_int):
        return random.randint(0, max_int)

    def get_rand_gif(self, gif_type="TEMPERATURE"):
        """
            Gets a random gif given a gif type from the gif_dicts

        """
        gif_links = gif_dict[gif_type]
        max_int = len(gif_links) - 1
        return gif_links[self.get_rand_int(max_int)]
