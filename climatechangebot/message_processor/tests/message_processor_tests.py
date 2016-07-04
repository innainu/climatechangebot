"""
    Tests for the Message Processor

    Run in directory with local config files
    > nosetests

"""

import unittest
import ConfigParser

from config import Config
from bot_interface.bot_interface import BotInterface
from message_processor.message_processor import WitParser, MessageProcessor
from nyt_interface.nyt_interface import NytimesApi

config = ConfigParser.ConfigParser()
config.read("local_test_config.cfg")

bot = BotInterface(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))
nyt_api = NytimesApi(config.get('NYTIMES', 'nyt_key'))
wit = WitParser(config.get('WITAI', 'wit_key'), bot, nyt_api)
Config = {'DEBUG': True}
msgproc = MessageProcessor(bot, wit, Config)
recipient_id = config.get('SECRET', 'fb_test_recipient_id')


class TestMessageProcessor(unittest.TestCase):

    def testParseMessageAttachment(self):
        message_with_attachment = {u'entry': [{u'messaging': [{u'timestamp': 1467596969812, u'message': {u'attachments': [{u'type': u'image', u'payload': {u'url': u'https://scontent.xx.fbcdn.net/t39.1997-6/p100x100/851586_126362014215262_1346191341_n.png?_nc_ad=z-m'}}], u'mid': u'mid.1467596969805:397b860aa7858f1995', u'seq': 699, u'sticker_id': 126362007548596}, u'recipient': {u'id': u'852964301474501'}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467596969833}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_attachment)
        self.assertEqual(response.status_code, 200)

    def testParseMessageText(self):
        message_with_text = {u'entry': [{u'messaging': [{u'timestamp': 1467598100136, u'message': {u'text': u'hey dude', u'mid': u'mid.1467598100129:66fdbf3421d1d4b345', u'seq': 706}, u'recipient': {u'id': u'852964301474501'}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598100153}], u'object': u'page'}
        response = msgproc.parse_messages(message_with_text)
        self.assertEqual(response.status_code, 200)

    def testParsePostback(self):
        message_was_delivered = {u'entry': [{u'messaging': [{u'delivery': {u'mids': [u'mid.1467598101099:5647b9af327a489557'], u'seq': 708, u'watermark': 1467598101124}, u'timestamp': 0, u'recipient': {u'id': u'852964301474501'}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467598101352}], u'object': u'page'}
        response = msgproc.parse_messages(message_was_delivered)
        self.assertIsNone(response)


class TestWitParser(unittest.TestCase):

    def testWitAPICall(self):
        sample_text = "hi"
        wit_parsed_message = wit.wit_api_call(sample_text)
        self.assertIsNotNone(wit_parsed_message)

    def testTakeActionNoIntent(self):
        t = {u'_text': u'hi', u'entities': {u'search_query': [{u'confidence': 0.743470030647855, u'suggested': True, u'type': u'value',
             u'value': u'hi'}]}, u'msg_id': u'1d129086-f7a6-4d24-a4fd-205a497e304b'}
        wit_parsed_message = wit.parse_wit_response(t, "hi")
        response = wit.wit_take_action(wit_parsed_message, recipient_id, num=1)
        self.assertEqual(response.status_code, 200)

    def testTakeActionNoIntentNoEntity(self):
        t = {u'_text': u'all', u'entities': {}, u'msg_id': u'd112c930-a596-41c6-9948-75c1a3de2234'}
        wit_parsed_message = wit.parse_wit_response(t, "all")
        response = wit.wit_take_action(wit_parsed_message, recipient_id, num=1)
        self.assertEqual(response.status_code, 200)

    def testTakeActionNoEntity(self):
        t = {u'_text': u'what articles', u'entities': {u'intent': [{u'confidence': 0.9920363903041917, u'value': u'search_article'}]},
             u'msg_id': u'e3ff388a-d8a7-436b-8499-94ba524c2d3a'}
        wit_parsed_message = wit.parse_wit_response(t, "what articles")
        response = wit.wit_take_action(wit_parsed_message, recipient_id, num=1)
        self.assertEqual(response.status_code, 200)

    def testTakeActionLowConfidence(self):
        """
            Intent and entity are present but with low confidence score
        """
        t = {u'_text': u'what article futh', u'entities': {u'intent': [{u'confidence': 0.44444, u'value': u'search_article'}],
             u'search_query': [{u'confidence': 0.4444444, u'suggested': True, u'type': u'value', u'value': u'futh'}]},
             u'msg_id': u'0d006d5a-aebe-46af-8252-908bc6cf6713'}
        wit_parsed_message = wit.parse_wit_response(t, "what article futh")
        response = wit.wit_take_action(wit_parsed_message, recipient_id, num=1)
        self.assertEqual(response.status_code, 200)

    def testTakeActionMultipleEntities(self):
        """
            Intent and entity are present but with low confidence score
        """
        t = {u'_text': u'articles about climate change and obama', u'entities': {u'intent': [{u'confidence': 0.8306483560746919, u'value': u'search_article'}],
             u'search_query': [{u'confidence': 0.8408922863637576, u'suggested': True, u'type': u'value', u'value': u'climate change'}, {u'confidence': 0.9926250080978738, u'suggested': True, u'type': u'value', u'value': u'obama'}]}, u'msg_id': u'413c6a34-1e93-479c-b3c0-58c12d99ff9c'}
        wit_parsed_message = wit.parse_wit_response(t, "articles about climate change and obama")
        response = wit.wit_take_action(wit_parsed_message, recipient_id, num=1)
        self.assertEqual(response.status_code, 200)

    def testCannotComputeCallback(self):
        response = wit.send_cannot_compute_helper_callback(recipient_id)
        self.assertEqual(response.status_code, 200)
