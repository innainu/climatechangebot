"""
    Tests for the Message Processor

    Run in directory with local config files
    > nosetests

"""

import os
import unittest
import ConfigParser

from config import Config
from rivescript import RiveScript
from bot_interface.bot_interface import BotInterface
from message_processor.message_processor import ExternalApiParser, MessageProcessor
from nyt_interface.nyt_interface import NytimesApi
from pymongo import MongoClient


config = ConfigParser.ConfigParser()
config.read("local_test_config.cfg")

bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))
nyt_api = NytimesApi(config.get('NYTIMES', 'nyt_key'))

rive = RiveScript()
rive.load_directory(
    os.path.join(os.path.dirname(__file__), "..", "rivescripts")
)
rive.sort_replies()

mongo = MongoClient()
mongo = mongo.app
external_api_parser = ExternalApiParser(config.get('WITAI', 'wit_key'),
                                        rive, bot, nyt_api, mongo)

Config = {'DEBUG': True, 'NYT_NUM_ARTICLES_RETURNED': 3}
msgproc = MessageProcessor(bot, external_api_parser, Config)
recipient_id = config.get('SECRET', 'fb_test_recipient_id')


class TestMessageProcessor(unittest.TestCase):

    def testParseMessageTextRive(self):

        message_with_text = {u'entry': [{u'messaging': [{u'timestamp': 1467598100136, u'message': {u'text': u'hey', u'mid': u'mid.1467598100129:66fdbf342d4b345', u'seq': 706}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598100153}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_text)
        self.assertEqual(response.status_code, 200)

    def testParseMessageAttachment(self):
        # Test attachment with unknown sticker
        message_with_attachment = {u'entry': [{u'messaging': [{u'timestamp': 1467596969812, u'message': {u'attachments': [{u'type': u'image', u'payload': {u'url': u'https://scontent.xx.fbcdn.net/t39.1997-6/p100x100/851586_126362014215262_1346191341_n.png?_nc_ad=z-m'}}], u'mid': u'mid.1467596969805:397b860aa7858f1994', u'seq': 699, u'sticker_id': 126362007548596}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467596969833}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_attachment)
        self.assertEqual(response.status_code, 200)

        # # Test attachment with known sticker
        # message_with_attachment = {u'entry': [{u'messaging': [{u'timestamp': 1467596969812, u'message': {u'attachments': [{u'type': u'image', u'payload': {u'url': u'https://scontent.xx.fbcdn.net/t39.1997-6/p100x100/851586_126362014215262_1346191341_n.png?_nc_ad=z-m'}}], u'mid': u'mid.1467596969805:397b860aa7858f1995', u'seq': 699, u'sticker_id': 369239343222814}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467596969833}], u'object': u'page'}
        # response = msgproc.parse_messages(message_with_attachment)
        # self.assertEqual(response.status_code, 200)

        # Test attachment without sticker
        message_with_attachment = {u'entry': [{u'messaging': [{u'timestamp': 1467596969812, u'message': {u'attachments': [{u'type': u'image', u'payload': {u'url': u'https://scontent.xx.fbcdn.net/t39.1997-6/p100x100/851586_126362014215262_1346191341_n.png?_nc_ad=z-m'}}], u'mid': u'mid.1467596969805:397b860aa7858f1996', u'seq': 699}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467596969833}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_attachment)
        self.assertEqual(response.status_code, 200)

    def testParsePostback(self):
        message_was_delivered = {u'entry': [{u'messaging': [{u'delivery': {u'mids': [u'mid.1467598101099:5647b9af327a489557'], u'seq': 708, u'watermark': 1467598101124}, u'timestamp': 0, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598101352}], u'object': u'page'}
        response = msgproc.parse_messages(message_was_delivered)
        self.assertIsNone(response)

    def testParsePostbackWelcomeMessage(self):
        # delete test user from mongo
        mongo.db.users.remove({'recipient_id': recipient_id})
        db_result = mongo.db.users.find_one({'recipient_id': recipient_id})
        self.assertIsNone(db_result)

        # Test the welcome message (WELCOME_MESSAGE_POSTBACK) for new user
        message_was_delivered = {u'entry': [{u'messaging': [{u'timestamp': 1469344026838, u'postback': {u'payload': u'WELCOME_MESSAGE_POSTBACK'}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': recipient_id, u'time': 1469344026838}], u'object': u'page'}
        response = msgproc.parse_messages(message_was_delivered)
        self.assertEqual(response.status_code, 200)

        # Test the welcome message (WELCOME_MESSAGE_POSTBACK) for an existing user
        existing_user = {u'recipient_id': recipient_id, u'user_vars': {u'first_name': u'First Name'}}
        mongo.db.users.insert_one(existing_user)
        message_was_delivered = {u'entry': [{u'messaging': [{u'timestamp': 1469344026838, u'postback': {u'payload': u'WELCOME_MESSAGE_POSTBACK'}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': recipient_id, u'time': 1469344026838}], u'object': u'page'}
        response = msgproc.parse_messages(message_was_delivered)
        self.assertEqual(response.status_code, 200)

        mongo.db.users.remove({'recipient_id': recipient_id})

    def testParsePostbackTrending(self):
        message_was_delivered = {u'entry': [{u'messaging': [{u'timestamp': 1469344026838, u'postback': {u'payload': u'TRENDING_POSTBACK'}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': recipient_id, u'time': 1469344026838}], u'object': u'page'}
        response = msgproc.parse_messages(message_was_delivered)
        self.assertEqual(response.status_code, 200)


class TestExternalWitApiParser(unittest.TestCase):

    def testWitAPICall(self):
        sample_text = "hi"
        wit_parsed_message = external_api_parser.wit_api_call(sample_text)
        self.assertIsNotNone(wit_parsed_message)

    def testTakeActionWitNoIntent(self):
        t = {u'_text': u'hi', u'entities': {u'search_query': [{u'confidence': 0.743470030647855, u'suggested': True, u'type': u'value',
             u'value': u'hi'}]}, u'msg_id': u'1d129086-f7a6-4d24-a4fd-205a497e304b'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("hi", recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionWitNoIntentNoEntity(self):
        t = {u'_text': u'all', u'entities': {}, u'msg_id': u'd112c930-a596-41c6-9948-75c1a3de2234'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("all", recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionWitNoEntity(self):
        t = {u'_text': u'what articles', u'entities': {u'intent': [{u'confidence': 0.9920363903041917, u'value': u'search_article'}]},
             u'msg_id': u'e3ff388a-d8a7-436b-8499-94ba524c2d3a'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("what articles", recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionLowConfidence(self):
        """
            Intent and entity are present but with low confidence score
        """
        t = {u'_text': u'what article futh', u'entities': {u'intent': [{u'confidence': 0.44444, u'value': u'search_article'}],
             u'search_query': [{u'confidence': 0.4444444, u'suggested': True, u'type': u'value', u'value': u'futh'}]},
             u'msg_id': u'0d006d5a-aebe-46af-8252-908bc6cf6713'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("what article futh", recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionMultipleEntities(self):
        """
            Intent and entity are present but with low confidence score
        """
        t = {u'_text': u'articles about climate change and obama', u'entities': {u'intent': [{u'confidence': 0.8306483560746919, u'value': u'search_article'}],
             u'search_query': [{u'confidence': 0.8408922863637576, u'suggested': True, u'type': u'value', u'value': u'climate change'}, {u'confidence': 0.9926250080978738, u'suggested': True, u'type': u'value', u'value': u'obama'}]}, u'msg_id': u'413c6a34-1e93-479c-b3c0-58c12d99ff9c'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("articles about climate change and obama",
                                                            recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionMultipleLocation(self):
        """
            Only location entity is present
        """
        t = {u'_text': u"I'm curious to see how climate change is affecting nyc and peru", u'entities': {u'intent': [{u'confidence': 0.9995201878399377,u'value': u'search_article'}],
             u'location': [{u'confidence': 0.7712675207275367,u'entities': {u'local_search_query': [{u'confidence': 0.9306302049390484,u'suggested': True,
             u'type': u'value',u'value': u'nyc'}]},u'suggested': True,u'type': u'value',u'value': u'nyc'},{u'confidence': 0.9306424865316572,u'entities': {},u'suggested': True,
             u'type': u'value',u'value': u'peru'}]},u'msg_id': u'04dba21c-80d3-4013-b07d-60e748df7a1e'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("I'm curious to see how climate change is affecting nyc and peru",
                                                            recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionSearchAndLocation(self):
        """
            Only location entity is present
        """
        t = {u'_text': u'i want to see articles about obama in nyc',u'entities': {u'intent': [{u'confidence': 0.998460645506234,u'value': u'search_article'}],u'location': [{u'confidence': 0.9942592382669772,
             u'entities': {u'local_search_query': [{u'confidence': 0.9306302049390484,u'suggested': True,u'type': u'value',u'value': u'nyc'}]},u'suggested': True,
             u'type': u'value',u'value': u'nyc'}],u'search_query': [{u'confidence': 0.9995756415635056,u'suggested': True,u'type': u'value',
             u'value': u'obama'}]},u'msg_id': u'95e1feb5-1e10-4d5a-ac88-b821a05b5b77'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action('i want to see articles about obama in nyc',
                                                            recipient_id, num_articles=3,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testTakeActionNYTReturnsNone(self):
        """
            NYT doesn't find any articles because search entities are too specific
        """
        t = {u'_text': u'blah blah', u'entities': {u'intent': [{u'confidence': 0.8306483560746919, u'value': u'search_article'}],
             u'search_query': [{u'confidence': 0.8408922863637576, u'suggested': True, u'type': u'value', u'value': u'sochestuka'}, {u'confidence': 0.9926250080978738, u'suggested': True, u'type': u'value', u'value': u'clanabapema'}]}, u'msg_id': u'413c6a34-1e93-479c-b3c0-58c12d99ff9c'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("blah blah",
                                                            recipient_id, num_articles=3,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)

    def testCannotComputeCallback(self):
        response = external_api_parser.send_cannot_compute_helper_callback(recipient_id)
        self.assertEqual(response.status_code, 200)

    def testTakeActionWitEntityLatest(self):
        t = {u'_text': u'trending', u'entities': {u'intent': [{u'confidence': 0.9920363903041917, u'value': u'latest'}]},
             u'msg_id': u'e3ff388a-d8a7-436b-8499-94ba524c2d3a'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("trending", recipient_id,
                                                            wit_parsed_message=wit_parsed_message,
                                                            rive_parsed_message="UNDEFINED_RESPONSE")
        self.assertEqual(response.status_code, 200)


class TestExternalRiveApiParser(unittest.TestCase):

    def testRiveCall(self):
        response = rive.reply(recipient_id, "hey")
        self.assertEqual(unicode, type(response))

    def testRiveUndefinedResponse(self):
        response = rive.reply(recipient_id, "alksdjf")
        self.assertEqual("UNDEFINED_RESPONSE", response)

    def testRiveUserDictFoundInDB(self):
        mongo.db.users.delete_many({'recipient_id': recipient_id})
        mongo.db.users.insert_one({'recipient_id': recipient_id})

        # test that response is 200 if user exists in db
        response = external_api_parser.take_external_action("hello", recipient_id, num_articles=3)
        self.assertEqual(response.status_code, 200)
        db_results = mongo.db.users.find({'recipient_id': recipient_id})
        db_results = [r for r in db_results]

        # make sure the record is unique in db
        self.assertEqual(len(db_results), 1)
        db_result = db_results[0]
        print(db_result)

        # test that record in db has the right keys
        self.assertTrue('__history__' in db_result['user_vars'].keys())
        self.assertTrue('__lastmatch__' in db_result['user_vars'].keys())
        mongo.db.users.remove({'recipient_id': recipient_id})

    def testRiveUserDictNotFoundInDB(self):

        mongo.db.users.remove({'recipient_id': recipient_id})
        db_result = mongo.db.users.find_one({'recipient_id': recipient_id})
        self.assertIsNone(db_result)

        # Test that response is 200 if user does not exist in db
        response = external_api_parser.take_external_action("hello", recipient_id, num_articles=3)
        self.assertEqual(response.status_code, 200)
        db_result = mongo.db.users.find({'recipient_id': recipient_id})

        # test that subsequent message with same user doesn't create new user in db
        response = external_api_parser.take_external_action("hello", recipient_id, num_articles=3)
        self.assertEqual(response.status_code, 200)
        db_results = mongo.db.users.find({'recipient_id': recipient_id})
        db_results = [r for r in db_results]
        self.assertEqual(len(db_results), 1)

        # test that the user has the right attributes in db
        db_result = db_results[0]
        self.assertTrue('__history__' in db_result['user_vars'].keys())
        self.assertTrue('__lastmatch__' in db_result['user_vars'].keys())
        self.assertEqual(db_result['user_vars']['first_name'], 'Baruch')

        mongo.db.users.remove({'recipient_id': recipient_id})


class TestKeywordExtraction(unittest.TestCase):

    def testGoodPOS(self):
        keywords = external_api_parser.extract_keywords("dogs")
        self.assertEqual(keywords, "dogs")
        keywords = external_api_parser.extract_keywords("dogs and cats")
        self.assertEqual(keywords, "dogs cats")
        keywords = external_api_parser.extract_keywords("dogs and cats and things galore")
        self.assertEqual(keywords, "dogs cats things galore")

    def testTooLong(self):
        keywords = external_api_parser.extract_keywords("dogs and cats and mice and things galore")
        self.assertEqual(keywords, None)

    def testBadPOS(self):
        keywords = external_api_parser.extract_keywords("can you tell me about dogs")
        self.assertEqual(keywords, None)

    def testEmoji(self):
        keywords = external_api_parser.extract_keywords(u"dogs \u26f2")
        self.assertEqual(keywords, "dogs")

    def testParseMessageTextKeyword(self):
        message_with_text = {u'entry': [{u'messaging': [{u'timestamp': 1467598100136, u'message': {u'text': u'trump', u'mid': u'mid.1467598100129:66fdbf3421d1d4b345', u'seq': 706}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598100153}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_text)
        self.assertEqual(response.status_code, 200)
