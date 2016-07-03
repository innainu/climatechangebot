"""
    Tests for the NYT Interface

    Run in directory with local config files
    > nosetests

"""

import unittest
import ConfigParser

from nyt_interface.nyt_interface import NytimesApi

config = ConfigParser.ConfigParser()
config.read("local_test_config.cfg")

NYT_API_KEY = config.get('NYTIMES', 'nyt_key')


class TestNYTInterface(unittest.TestCase):

    def testReturnArticleList(self):
        api = NytimesApi(NYT_API_KEY)
        articles = api.return_article_list('africa')
        self.assertIsInstance(articles, list)
        self.assertEqual(len(articles), 1)

    def testReturnArticleListMultiple(self):
        api = NytimesApi(NYT_API_KEY)
        articles = api.return_article_list('africa', num=4)
        self.assertIsInstance(articles, list)
        self.assertEqual(len(articles), 4)
