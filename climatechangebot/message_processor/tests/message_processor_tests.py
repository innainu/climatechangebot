"""
    Tests for the Message Processor

    Run in directory with local config files
    > nosetests

"""

import unittest

from message_processor.message_processor import MessageProcessor


class TestMessageProcessor(unittest.TestCase):

    def testParseMessageText(self):
        message = {u'entry': [{u'messaging': [{u'delivery': {u'mids': [u'mid.1467561011579:1930a4585d9ce5f569'], u'seq': 468, u'watermark': 1467561011696}, u'timestamp': 0, u'recipient': {u'id': u'852964301474501'}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467561012087}], u'object': u'page'}

        api = NytimesApi(NYT_API_KEY)
        articles = api.return_article_list('africa')
        self.assertIsInstance(articles, list)

    def testParseMessageAttachment(self):
        api = NytimesApi(NYT_API_KEY)
        articles = api.return_article_list('africa')
        self.assertIsInstance(articles, list)

    def testParseMessageText(self):
        message = {u'entry': [{u'messaging': [{u'delivery': {u'mids': [u'mid.1467561011579:1930a4585d9ce5f569'], u'seq': 468, u'watermark': 1467561011696}, u'timestamp': 0, u'recipient': {u'id': u'852964301474501'}, u'sender': {u'id': u'986080158173463'}}], u'id': u'852964301474501', u'time': 1467561012087}], u'object': u'page'}
