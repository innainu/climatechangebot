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

config = ConfigParser.ConfigParser()
config.read("local_test_config.cfg")

bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))
nyt_api = NytimesApi(config.get('NYTIMES', 'nyt_key'))

rive = RiveScript()
rive.load_directory(
    os.path.join(os.path.dirname(__file__), "..", "rivescripts")
)
rive.sort_replies()

external_api_parser = ExternalApiParser(config.get('WITAI', 'wit_key'),
                                        rive, bot, nyt_api)

Config = {'DEBUG': True, 'NYT_NUM_ARTICLES_RETURNED': 3}
msgproc = MessageProcessor(bot, external_api_parser, Config)
recipient_id = config.get('SECRET', 'fb_test_recipient_id')


class TestMessageProcessor(unittest.TestCase):

    def testParseMessageAttachment(self):
        message_with_attachment = {u'entry': [{u'messaging': [{u'timestamp': 1467596969812, u'message': {u'attachments': [{u'type': u'image', u'payload': {u'url': u'https://scontent.xx.fbcdn.net/t39.1997-6/p100x100/851586_126362014215262_1346191341_n.png?_nc_ad=z-m'}}], u'mid': u'mid.1467596969805:397b860aa7858f1995', u'seq': 699, u'sticker_id': 126362007548596}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467596969833}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_attachment)
        self.assertEqual(response.status_code, 200)

    def testParseMessageText(self):
        message_with_text = {u'entry': [{u'messaging': [{u'timestamp': 1467598100136, u'message': {u'text': u'hey dude', u'mid': u'mid.1467598100129:66fdbf3421d1d4b345', u'seq': 706}, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598100153}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_text)
        self.assertEqual(response.status_code, 200)

    def testParsePostback(self):
        message_was_delivered = {u'entry': [{u'messaging': [{u'delivery': {u'mids': [u'mid.1467598101099:5647b9af327a489557'], u'seq': 708, u'watermark': 1467598101124}, u'timestamp': 0, u'recipient': {u'id': recipient_id}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598101352}], u'object': u'page'}
        response = msgproc.parse_messages(message_was_delivered)
        self.assertIsNone(response)


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
                                                            wit_parsed_message=wit_parsed_message)
        self.assertEqual(response.status_code, 200)

    def testTakeActionWitNoIntentNoEntity(self):
        t = {u'_text': u'all', u'entities': {}, u'msg_id': u'd112c930-a596-41c6-9948-75c1a3de2234'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("all", recipient_id,
                                                            wit_parsed_message=wit_parsed_message)
        self.assertEqual(response.status_code, 200)

    def testTakeActionWitNoEntity(self):
        t = {u'_text': u'what articles', u'entities': {u'intent': [{u'confidence': 0.9920363903041917, u'value': u'search_article'}]},
             u'msg_id': u'e3ff388a-d8a7-436b-8499-94ba524c2d3a'}
        wit_parsed_message = external_api_parser.parse_wit_response(t)
        response = external_api_parser.take_external_action("what articles", recipient_id,
                                                            wit_parsed_message=wit_parsed_message)
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
                                                            wit_parsed_message=wit_parsed_message)
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
                                                            wit_parsed_message=wit_parsed_message)
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
                                                            wit_parsed_message=wit_parsed_message)
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
                                                            wit_parsed_message=wit_parsed_message)
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
                                                            wit_parsed_message=wit_parsed_message)
        self.assertEqual(response.status_code, 200)

    def testCannotComputeCallback(self):
        response = external_api_parser.send_cannot_compute_helper_callback(recipient_id)
        self.assertEqual(response.status_code, 200)


# class TestExternalApiAIParser(unittest.TestCase):

#     def testApiAICall(self):
#         sample_text = "hi"
#         api_ai_parsed_message = external_api_parser.api_ai_call(sample_text)
#         self.assertIsNotNone(api_ai_parsed_message)

#     def testApiAIStatus400(self):
#         sample_text = ""
#         api_ai_parsed_message = external_api_parser.api_ai_call(sample_text)
#         self.assertEqual(api_ai_parsed_message.response_text, None)
#         self.assertEqual(api_ai_parsed_message.action, None)

#     def testTakeActionApiAICall(self):
#         """
#             Test that API.ai call works after Wit.ai returns nothing
#         """
#         t = {u'_text': u'all', u'entities': {}, u'msg_id': u'd112c930-a596-41c6-9948-75c1a3de2234'}
#         wit_parsed_message = external_api_parser.parse_wit_response(t)
#         response = external_api_parser.take_external_action("who are you", recipient_id,
#                                                             wit_parsed_message=wit_parsed_message)
#         self.assertEqual(response.status_code, 200)

#     def testTakeActionApiAIIntegration(self):
#         """
#             Tests that API.ai response text can be sent to user without making an API call to APi.ai
#         """
#         t = {u'_text': u'all', u'entities': {}, u'msg_id': u'd112c930-a596-41c6-9948-75c1a3de2234'}
#         t2 = {u'status': {u'errorType': u'success', u'code': 200}, u'timestamp': u'2016-07-04T20:19:44.497Z', u'sessionId': u'5fe142b5e1cd4b96a5c8eff478084601', u'id': u'cb076b89-23fc-4290-b0c9-d18965ba94cd', u'result': {u'parameters': {u'simplified': u'who are you'}, u'resolvedQuery': u'Who are you?', u'source': u'domains', u'score': 0.0, u'fulfillment': {u'speech': u'climatechangebot'}, u'action': u'smalltalk.person', u'metadata': {}}}
#         wit_parsed_message = external_api_parser.parse_wit_response(t)
#         api_ai_parsed_message = external_api_parser.parse_api_ai_response(t2)
#         response = external_api_parser.take_external_action("who are you", recipient_id,
#                                                             wit_parsed_message=wit_parsed_message,
#                                                             api_ai_parsed_message=api_ai_parsed_message)
#         self.assertEqual(response.status_code, 200)
