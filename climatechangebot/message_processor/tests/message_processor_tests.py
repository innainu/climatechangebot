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
msgproc = MessageProcessor(bot, wit, Config)


class TestMessageProcessor(unittest.TestCase):

    def testTest(self):
        self.assertEqual(1, 1)
