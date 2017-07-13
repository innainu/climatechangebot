import facebook
from nyt_interface.nyt_interface import NytimesApi
import ConfigParser


def post_latest():
    config = ConfigParser.ConfigParser()
    config.read("local_test_config.cfg")
    NYT_API_KEY = config.get('NYTIMES', 'nyt_key')
    FB_ACCESS_TOKEN = config.get('SECRET', 'INNA_ACCESS_TOKEN')

    nyt_api = NytimesApi(NYT_API_KEY)
    trending_articles = nyt_api.return_trending_list()
    trending_articles = sorted(trending_articles, key=lambda x: x['date'])
    trending_article = trending_articles[-1]

    graph = facebook.GraphAPI(FB_ACCESS_TOKEN)
    message = 'This is an automated message from m.me/climatechangebot. Check out this article about climate change.'
    graph.put_object(
        "me", "feed",
        message=message, link=trending_article['web_url'],
        picture=trending_article['image_url'])


if __name__ == '__main__':
    print post_latest()
