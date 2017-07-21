import facebook
import ConfigParser
import os

from nyt_interface.nyt_interface import NytimesApi


def post_latest():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(cur_dir, "local_test_config.cfg")

    config = ConfigParser.ConfigParser()
    config.read(config_path)
    NYT_API_KEY = config.get('NYTIMES', 'nyt_key')
    FB_ACCESS_TOKEN = config.get('SECRET', 'INNA_ACCESS_TOKEN')

    nyt_api = NytimesApi(NYT_API_KEY)
    trending_articles = nyt_api.return_trending_list()
    trending_articles = sorted(trending_articles, key=lambda x: x['date'])
    trending_article = trending_articles[0]

    graph = facebook.GraphAPI(FB_ACCESS_TOKEN)
    message = 'This is an automated message from m.me/climatechangebot. Check out this article about climate change.'
    graph.put_object(
        "me", "feed",
        message=message, link=trending_article['web_url'],
        picture=trending_article.get('image_url', None))


if __name__ == '__main__':
    print post_latest()
