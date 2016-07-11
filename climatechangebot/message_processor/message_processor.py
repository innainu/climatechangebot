"""
    Message processor - the heart of our robot

    Parse messages from Facebook:
        https://developers.facebook.com/docs/messenger-platform/webhook-reference


    TO DO:
        - Remove dependencies on API.ai with home grown conversational toolkit
        - Build out Wit.ai search functionaility
        - Make caching of messages more sophisticated
"""

import time
import random
import bot_response_text
import response_dicts

from wit import Wit
from wit.wit import WitError
# import apiai

from models.user import User
from bot_interface.bot_interface import ButtonType, SenderActions


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


class ApiAIParsedMessage(object):
    def __init__(self):
        self.action = None
        self.response_text = None


class WitParsedMessage():
    def __init__(self):
        self.intent = None
        self.search_queries = []
        self.locations = []

    def has_at_least_one_entity(self):
        if len(self.search_queries) > 0 or len(self.locations) > 0:
            return True
        return False


class ExternalApiParser(object):
    """
        This calls external APIs for responses.
        api.ai  for conversational queries
        wit.ai for entities and intents
            - each entity gets a confidence value from 0 to 1.
                "1 is extremely confident. Lower than 0.5 is considered very low confidence."
            - can add intents using api:
            https://wit.ai/docs/http/20160330#get-intent-via-text-link
            - self.actions : this is for merge and context functionality
    """

    def __init__(self, wit_key, rive, bot, nyt_api, mongo):
        self.BOT = bot
        self.NYT_API = nyt_api

        self.wit_actions = {}
        self.wit_client = Wit(access_token=wit_key, actions=self.wit_actions)
        self.wit_empty_response = {'entities': []}
        self.WIT_SEARCH_QUERY_CONFIDENCE_THRESH = 0.5

        self.RIVE = rive

        self.MONGO = mongo

        # self.api_ai = apiai.ApiAI(api_ai_key)
        # self.API_AI_LANG = 'en'
        # self.api_ai_empty_response = {'result': {'fulfillment': {'speech': u''}}}

    # def api_ai_call(self, text):
    #     try:
    #         api_ai_request = self.api_ai.text_request()
    #         api_ai_request.lang = self.API_AI_LANG
    #         api_ai_request.query = text
    #         api_ai_response = json.loads(api_ai_request.getresponse().read())
    #         status_code = api_ai_response['status']['code']
    #         if status_code != 200:
    #             api_ai_response = self.api_ai_empty_response

    #     except Exception as e:
    #         print(e)
    #         api_ai_response = self.api_ai_empty_response

    #     api_ai_parsed_message = self.parse_api_ai_response(api_ai_response)
    #     return api_ai_parsed_message

    # def parse_api_ai_response(self, api_ai_response):
    #     api_ai_parsed_message = ApiAIParsedMessage()
    #     api_ai_result = api_ai_response['result']

    #     if 'action' in api_ai_result:
    #         api_ai_parsed_message.action = api_ai_result['action']
    #     else:
    #         api_ai_parsed_message.action = None

    #     # the following keys are always included, empty if there is no response.
    #     if 'fulfillment' in api_ai_result and 'speech' in api_ai_result['fulfillment']\
    #             and len(api_ai_result['fulfillment']['speech']) > 0:
    #         api_ai_parsed_message.response_text = api_ai_result['fulfillment']['speech']

    #     return api_ai_parsed_message

    def wit_api_call(self, text):
        try:
            wit_response = self.wit_client.message(text)
        except WitError as we:
            print(we)
            # the Wit API call failed due to a WitError, so let's make the response empty
            wit_response = self.wit_empty_response

        wit_parsed_message = self.parse_wit_response(wit_response)
        return wit_parsed_message

    def parse_wit_response(self, wit_return_dict):
        """
            Takes a Wit response dict and converts into a WitParsedMessage object
        """

        wit_entities = wit_return_dict['entities']
        wit_parsed_message = WitParsedMessage()

        intent = None
        if 'intent' in wit_entities:
            intent = (wit_entities['intent'][0]['value'], wit_entities['intent'][0]['confidence'])
        wit_parsed_message.intent = intent

        search_queries = []
        if 'search_query' in wit_entities:
            for search_query in wit_entities['search_query']:
                search_queries.append((search_query['value'], search_query['confidence']))
        wit_parsed_message.search_queries = search_queries

        locations = []
        if 'location' in wit_entities:
            for loc in wit_entities['location']:
                locations.append((loc['value'], loc['confidence']))
        wit_parsed_message.locations = locations

        return wit_parsed_message

    def take_external_action(self, message_text, recipient_id, num_articles=1,
                             wit_parsed_message=None, rive_parsed_message=None):
        """
            Sends messages to the user.
            if Wit Parser finds intent, return on behalf of wit.ai
            else returns on behalf of api.ai
            else returns helper callback

            params:
                message_text: str or unicode
                recipient_id: str
                num_articles: int
                wit_parsed_message: WitParsedMessage
                api_ai_parsed_message: ApiAIParsedMessage - DEPRECATED
                rive_parsed_message: str

            returns:
                http response
        """

        # Search RIVE for a valid response
        if rive_parsed_message is None:
            # get user info from the db
            user = User()
            user_dict = self.MONGO.db.users.find_one({'recipient_id': recipient_id})

            print('User dict is: ', user_dict)

            if user_dict is None:
                # get user information from Facebook
                fb_user_profile_info = self.BOT.get_user_profile_info(recipient_id)
                user.set_user_dict(recipient_id, fb_user_profile_info, timestamp=int(time.time()))

                # write the user information to our database
                self.MONGO.db.users.insert_one(user.user_dict)
                user_dict = user.user_dict
            else:
                user.user_dict = user_dict

            # give rivescript our user_vars
            if user_dict.get('user_vars'):
                for key, value in user_dict['user_vars'].items():
                    self.RIVE.set_uservar(recipient_id, key, value)

            # get the rivescript response
            rive_parsed_message = self.RIVE.reply(recipient_id, message_text)

            # get all the user vars back out of the RIVE to insert into DB
            new_user_vars = self.RIVE.get_uservars(recipient_id)
            user.update_user_vars(new_user_vars)
            self.MONGO.db.users.update({'recipient_id': recipient_id}, user.user_dict)

            print('New user vars are: ', user.user_dict)

        if rive_parsed_message != "UNDEFINED_RESPONSE":
            response = self.BOT.send_text_message(recipient_id, rive_parsed_message)
            return response

        # Rive had UNDEFINED_RESPONSE, so let's search WIT.AI for a response
        if wit_parsed_message is None:
            wit_parsed_message = self.wit_api_call(message_text)

        # Parse the WIT.AI response
        if wit_parsed_message.intent and wit_parsed_message.intent[0] == 'search_article' \
                and wit_parsed_message.intent[1] > self.WIT_SEARCH_QUERY_CONFIDENCE_THRESH \
                and wit_parsed_message.has_at_least_one_entity():

            nyt_query_string = ""
            # take entitiy with highest confidence
            if len(wit_parsed_message.search_queries) > 0:
                query = sorted(wit_parsed_message.search_queries, key=lambda x: x[1], reverse=True)[0]
                nyt_query_string += query[0]

            if len(wit_parsed_message.locations) > 0:
                location = sorted(wit_parsed_message.locations, key=lambda x: x[1], reverse=True)[0]
                nyt_query_string += " in " + location[0]

            # Get NYT articles to send to user
            nyt_response = self.NYT_API.return_article_list(nyt_query_string, num=num_articles)

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

            # if NYT api returns valid articles, then send them to the user
            if len(template_elements) > 0:
                response = self.BOT.send_text_message(recipient_id, "Here are some articles for you:")
                response = self.BOT.send_generic_payload_message(recipient_id, elements=template_elements)
                return response

        # nyt api returned nothing or Wit couldn't parse user message
        # so call api.ai
        # if api_ai_parsed_message is None:
            # api_ai_parsed_message = self.api_ai_call(message_text)

        # if api_ai_parsed_message.response_text is not None:
            # response = self.BOT.send_text_message(recipient_id, api_ai_parsed_message.response_text)
            # return response

        # Wit.ai and Rive couldn't compute a valid response, so return a helper callback
        response = self.send_cannot_compute_helper_callback(recipient_id)
        return response

    def send_cannot_compute_helper_callback(self, recipient_id):
        help_button = self.BOT.create_button(
            button_type=ButtonType.POSTBACK.value, title="Help",
            payload="HELP_POSTBACK"
        )

        response = self.BOT.send_button_payload_message(
            recipient_id,
            button_title=bot_response_text.help_button_title,
            buttons=[help_button]
        )

        return response


class MessageProcessor(object):
    """
        Processes incoming messages from Facebook and directs functionaility
            to WitParser or other parsing objects that send responses back to the user
    """

    def __init__(self, bot, external_api_parser, config):
        self.BOT = bot
        self.EXTERNAL_API_PARSER = external_api_parser
        self.CONFIG = config
        self.cache_message_ids = []

    def parse_messages(self, messages):
        """
            Parses messages from Facebook as they come in, and chooses which actions
            to execute depending on the message type


            :rtype: response from requests.post() method
        """
        print('debug is ' + str(self.CONFIG['DEBUG']))
        if self.CONFIG['DEBUG']:
            print(messages)

        # this is a really simple caching scheme, we should probably fix it later
        if len(self.cache_message_ids) > 200:
            self.cache_message_ids = self.cache_message_ids[-100:]

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

                    if message.message_id in self.cache_message_ids:
                        continue

                    self.cache_message_ids.append(message.message_id)
                    # We are assuming that a message has either a text payload or an image payload
                    #   but not both
                    if message.message_text:
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_ON.value)
                        #call witprocessor here
                        # wit_parsed_message = self.API_PARSER.wit_api_call(message.message_text)
                        response = self.EXTERNAL_API_PARSER.take_external_action(
                            message.message_text, recipient_id,
                            self.CONFIG['NYT_NUM_ARTICLES_RETURNED']
                        )
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_OFF.value)

                    elif message.message_attachments:
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_ON.value)
                        # send a random gif
                        gif_attachment_url = self.get_rand_gif()
                        response = self.BOT.send_image_payload_message(recipient_id,
                                                                       image_url=gif_attachment_url)
                        self.BOT.send_sender_action(recipient_id, SenderActions.TYPING_OFF.value)

                elif m.get('postback'):
                    """
                        Someone clicks on a postback message we sent
                    """

                    postback_payload = m['postback']['payload']
                    if self.CONFIG['DEBUG']:
                        print('got postback %s' % postback_payload)

                    response = self.postback_parser(recipient_id, postback_payload)
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
                    # mid_array = delivery['mids']
                    if self.CONFIG['DEBUG']:
                        print('got message delivery notification for %s' % str(delivery))
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

    def postback_parser(self, recipient_id, postback_payload):
        response = None
        if postback_payload == "HELP_POSTBACK":
            response = self.BOT.send_text_message(recipient_id, bot_response_text.help_postback_text)

        return response

    def get_rand_int(self, max_int):
        return random.randint(0, max_int)

    def get_rand_gif(self, gif_type="TEMPERATURE"):
        """
            Gets a random gif given a gif type from the gif_dicts

        """
        gif_links = response_dicts.gif_dict[gif_type]
        max_int = len(gif_links) - 1
        return gif_links[self.get_rand_int(max_int)]
