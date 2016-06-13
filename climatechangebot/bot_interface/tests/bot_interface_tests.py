"""
    Tests for the Facebook Messenger Bot Interface

    Run in directory with local config files
    > nosetests

"""

import unittest
import ConfigParser

from config import Config
from bot_interface.bot_interface import NotificationType, RecipientMethod, BotInterface

config = ConfigParser.ConfigParser()
config.read("local_test_config.cfg")

FB_MESSAGING_URL = (
    "https://graph.facebook.com"
    "/v{0}/me/messages?access_token={1}"
).format(Config.FB_API_VERSION, config.get('SECRET', 'fb_access_token'))


class TestBotInterface(unittest.TestCase):
    def testNotificationTypeEnum(self):
        self.assertEqual(NotificationType.REGULAR.value, "REGULAR")
        self.assertEqual(NotificationType.SILENT_PUSH.value, "SILENT_PUSH")
        self.assertEqual(NotificationType.NO_PUSH.value, "NO_PUSH")

    def testRecipientMethodEnum(self):
        self.assertEqual(RecipientMethod.ID.value, "id")
        self.assertEqual(RecipientMethod.PHONE_NUMBER.value, "phone_number")

    def testBotInterfaceInit(self):
        bot = BotInterface(FB_MESSAGING_URL)
        self.assertIsNotNone(bot)

    def testSendTextMessage(self):
        bot = BotInterface(FB_MESSAGING_URL)
        response = bot.send_text_message(config.get('SECRET', 'fb_test_recipient_id'),
            'Testing the bot interface testSendTextMessage', RecipientMethod.ID.value,
            NotificationType.REGULAR.value)

        self.assertEqual(response.status_code, 200)
